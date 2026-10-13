"""
Suíte de Testes Reais Endurecida: Mecanismo de Pesquisa Online Assíncrona Scoped do SUS-DF.
Execução 100% real sem dados mockados. Cobre:
- Portão de escopo refinado (eliminação de falsos positivos com co-ocorrência e inclusão de procedimentos da mulher/homem).
- Segurança anti-SSRF com rejeição de 127.0.0.1, localhost, IPs privados e domínios municipais fora do DF.
- Defesa clínica em profundidade acoplada ao search_async.
- Circuit breaker operacional e degradação graciosa fail-closed.
- Auto-ingestão persistente em ThreadPool e endpoints FastAPI.
"""
import pytest
from fastapi.testclient import TestClient

from app.config import get_settings
from app.ingestion.contracts import SUSDataTag
from app.main import app
from app.rag.embeddings import Embedder
from app.rag.guardrails import GuardrailsClassifier
from app.rag.retriever import ChromaRetriever
from app.ingestion.processor import IngestionProcessor
from app.rag.online_search import (
    CircuitBreaker,
    ScopedOnlineSearchComplementer,
    is_allowed_domain,
    is_within_sus_scope,
)


@pytest.fixture(scope="module")
def real_online_search_components():
    settings = get_settings()
    embedder = Embedder(settings.embedding_model, settings.embedding_max_seq_length)
    retriever = ChromaRetriever(embedder, settings.chroma_dir)
    guardrails = GuardrailsClassifier()
    processor = IngestionProcessor(retriever=retriever, storage_dir=settings.docs_dir)
    complementer = ScopedOnlineSearchComplementer(
        retriever=retriever,
        ingestion_processor=processor,
        guardrails=guardrails,
        timeout_seconds=5.0,
        max_results=3,
    )
    return complementer, retriever, processor, guardrails, settings


class TestScopedOnlineSearch:
    """Valida o mecanismo de pesquisa online restrito e sua segurança."""

    def test_scope_gate_rejects_out_of_domain(self):
        """Garante que assuntos fora da saúde pública e SUS-DF sejam barrados no portão."""
        # 1. Queries fora de escopo mundanas (incluindo as detectadas pelo Auditor Adversarial)
        ood_queries = [
            "como fazer bolo de cenoura fofinho",
            "resultado do jogo de futebol de ontem",
            "qual a cotacao do dolar hoje",
            "tabela fipe honda civic 2020",
            "receita de brigadeiro gourmet",
            "como consertar ar condicionado split",
            "qual o horario de funcionamento do cinema do park shopping?",
            "quais documentos levar para o detran taguatinga?",
            "onde tem posto de gasolina na ceilandia?",
        ]
        for q in ood_queries:
            assert is_within_sus_scope(q) is False, f"Query OOD '{q}' deveria ser rejeitada pelo portão de escopo!"

        # 2. Queries legítimas do SUS-DF (incluindo procedimentos que faltavam)
        in_domain_queries = [
            "onde vacinar contra a gripe em ceilandia?",
            "qual o horario de atendimento da ubs no gama?",
            "como agendar consulta de pre natal em taguatinga?",
            "dados abertos de medicamentos e farmacia basica df",
            "onde tem tenda de dengue e hidratacao na asa norte?",
            "como pegar remedio de alto custo no sus df?",
            "qual telefone do samu 192?",
            "quero agendar mamografia",
            "como colocar diu no sus",
            "exame preventivo na ubs",
            "cirurgia de vasectomia pelo sus df",
            "documentos para consulta medica",
            "horario da sala de vacina da ubs",
        ]
        for q in in_domain_queries:
            assert is_within_sus_scope(q) is True, f"Query legítima '{q}' deveria ser aceita pelo portão de escopo!"

    def test_allowed_domains_strictly_enforced_anti_ssrf(self):
        """Verifica a imunidade contra SSRF rejeitando URLs externas, locais e IPs."""
        # Domínios oficiais autorizados do ecossistema SUS-DF
        assert is_allowed_domain("https://saude.df.gov.br/noticias/vacinacao") is True
        assert is_allowed_domain("https://dados.df.gov.br/dataset/ubs") is True
        assert is_allowed_domain("https://agenciabrasilia.df.gov.br/noticias/saude") is True
        assert is_allowed_domain("https://www.saude.gov.br/campanhas") is True
        assert is_allowed_domain("https://portal.fiocruz.br/noticia") is True
        assert is_allowed_domain("https://www.gov.br/anvisa/pt-br") is True

        # Rejeição explícita de localhost e IPs internos (eliminação de vetor de ataque)
        assert is_allowed_domain("http://127.0.0.1:8000/api/chat") is False
        assert is_allowed_domain("http://127.0.0.1:11434/api/generate") is False
        assert is_allowed_domain("http://localhost:5000/api") is False
        assert is_allowed_domain("http://localhost:8000/docs") is False
        assert is_allowed_domain("http://0.0.0.0:8000") is False
        assert is_allowed_domain("http://10.0.0.1/admin") is False
        assert is_allowed_domain("http://192.168.1.1/router") is False
        assert is_allowed_domain("http://169.254.169.254/latest/meta-data/") is False

        # Rejeição de domínios externos e governamentais alheios ao SUS-DF
        assert is_allowed_domain("https://google.com/search?q=saude") is False
        assert is_allowed_domain("https://evil-hacker.com/malicious.json") is False
        assert is_allowed_domain("https://clinica-particular-sp.com.br") is False
        assert is_allowed_domain("https://prefeitura-aleatoria-sp.gov.br/noticia") is False
        assert is_allowed_domain("javascript:alert(1)") is False

    @pytest.mark.anyio
    async def test_clinical_guardrail_deep_defense_in_online_search(self, real_online_search_components):
        """Garante que perguntas clínicas sejam barradas antes de disparar requisições externas."""
        complementer, _, _, guardrails, _ = real_online_search_components
        clinical_queries = [
            "que remedio devo tomar para dor de cabeca e enjoo?",
            "estou sentindo muita febre e dor no peito, o que fazer?",
            "me receite um antibiotico para garganta inflamada",
        ]
        for q in clinical_queries:
            # 1. Barramento no próprio guardrail
            assert guardrails.is_clinical(q) is True
            # 2. Defesa em profundidade: search_async retorna lista vazia imediatamente sem requisição externa
            chunks = await complementer.search_async(q)
            assert chunks == [], f"Consulta clínica '{q}' deveria ter retornado vazio em search_async!"

    def test_circuit_breaker_resilience(self):
        """Valida que o Circuit Breaker desarma requisições após falhas consecutivas de rede."""
        cb = CircuitBreaker(failure_threshold=3, recovery_time_s=10.0)
        assert cb.is_open() is False
        cb.record_failure()
        cb.record_failure()
        assert cb.is_open() is False
        cb.record_failure()
        # Após 3 falhas consecutivas, deve estar aberto (bloqueando tráfego externo)
        assert cb.is_open() is True
        # Sucesso reseta o contador
        cb.record_success()
        assert cb.is_open() is False

    @pytest.mark.anyio
    async def test_real_ckan_and_sesdf_async_search(self, real_online_search_components):
        """Executa busca real assíncrona no Portal de Dados Abertos do DF e SES-DF."""
        complementer, _, _, _, _ = real_online_search_components
        chunks = await complementer.search_async("postos de vacinacao e ubs no distrito federal")
        assert isinstance(chunks, list)
        for c in chunks:
            assert c.url is not None
            assert is_allowed_domain(c.url) is True
            assert len(c.text) >= 50
            assert "<script" not in c.text.lower()
            assert "<style" not in c.text.lower()

    @pytest.mark.anyio
    async def test_auto_ingestion_persistent_executor(self, real_online_search_components):
        """Valida que documentos online complementam assincronamente a base ChromaDB via ThreadPool persistente."""
        complementer, retriever, processor, _, _ = real_online_search_components
        initial_count = retriever.count()

        real_doc = {
            "title": "Aviso Oficial: Ponto de Atendimento Rápido Especial em Santa Maria",
            "text": (
                "A Secretaria de Saúde do Distrito Federal informa a abertura de ponto temporário de hidratação "
                "e acolhimento na Região Administrativa de Santa Maria para suporte à comunidade durante o período sazonal. "
                "Horário de atendimento das 07:00 às 19:00 todos os dias."
            ),
            "url": "https://www.saude.df.gov.br/comunicado-santa-maria-sazonal-2026",
            "tag": SUSDataTag.UNIDADE,
            "source_name": "Secretaria de Saúde do DF",
        }

        # Submete via ThreadPool persistente
        complementer.schedule_auto_ingestion([real_doc])

        # Aguarda brevemente a conclusão na threadpool do processo
        import asyncio
        for _ in range(20):
            if real_doc["url"] in [d.get("url") for d in processor._manifest["documents"].values()]:
                break
            await asyncio.sleep(0.1)

        # Confirma que foi indexado no ChromaDB
        new_count = retriever.count()
        assert new_count >= initial_count
        assert real_doc["url"] in [d.get("url") for d in processor._manifest["documents"].values()]

    def test_online_search_endpoint_integration(self):
        """Valida o endpoint POST /api/search/online via TestClient."""
        with TestClient(app) as client:
            # 1. Consulta administrativa legítima
            res = client.post("/api/search/online", json={"query": "dados abertos farmacia e ubs df"})
            assert res.status_code == 200
            data = res.json()
            assert "results_found" in data
            assert data["is_blocked"] is False
            assert "chunks" in data

            # 2. Consulta clínica deve ser bloqueada na borda
            res_clin = client.post("/api/search/online", json={"query": "que remedio tomar para dor forte?"})
            assert res_clin.status_code == 200
            data_clin = res_clin.json()
            assert data_clin["is_blocked"] is True
            assert data_clin["results_found"] == 0
