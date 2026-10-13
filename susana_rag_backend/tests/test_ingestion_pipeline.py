"""Testes automatizados do pipeline autônomo de ingestão e webhooks do SUS."""
import json
import pytest
from fastapi.testclient import TestClient

from app.ingestion.contracts import RawDocumentPayload, SUSDataTag, IngestionResult
from app.ingestion.processor import IngestionProcessor
from app.ingestion.scraper import SUSAutonomousScraper, classify_tag
from app.ingestion.webhook import set_processor
from app.main import app


@pytest.fixture
def temp_processor(tmp_path):
    proc = IngestionProcessor(retriever=None, storage_dir=tmp_path)
    set_processor(proc)
    return proc


def test_contracts_validate_fields_correctly():
    # Payload válido
    payload = RawDocumentPayload(
        title="Novo Calendário de Vacinação da Dengue 2026",
        text="A Secretaria de Saúde do DF inicia a vacinação contra a dengue para crianças e jovens.",
        source_url="https://www.saude.df.gov.br/vacinacao-dengue",
        tag=SUSDataTag.VACINACAO,
    )
    assert payload.tag == SUSDataTag.VACINACAO
    assert "saude.df.gov.br" in str(payload.source_url)


def test_contracts_reject_invalid_urls():
    with pytest.raises(ValueError):
        RawDocumentPayload(
            title="Título de Teste",
            text="Texto com tamanho suficiente para validar o contrato mínimo de cinquenta caracteres.",
            source_url="ftp://invalido.com",
            tag=SUSDataTag.INSTITUCIONAL,
        )


def test_processor_deduplicates_by_hash(temp_processor):
    payload = RawDocumentPayload(
        title="Comunicado Oficial de Farmácias",
        text="Este comunicado informa sobre o estoque de medicamentos nas unidades do Distrito Federal.",
        source_url="https://www.saude.df.gov.br/comunicado-farmacia",
        tag=SUSDataTag.MEDICAMENTO,
    )

    # Primeira ingestão -> Sucesso
    res1 = temp_processor.process_document(payload)
    assert res1.status == "success"
    assert res1.is_duplicate is False
    assert res1.chunks_created >= 1

    # Segunda ingestão idêntica -> Ignorado por duplicidade
    res2 = temp_processor.process_document(payload)
    assert res2.status == "skipped"
    assert res2.is_duplicate is True
    assert res2.chunks_created == 0


def test_webhook_requires_valid_api_key():
    client = TestClient(app)
    payload_dict = {
        "title": "Nota Técnica sobre Soros Antiofídicos",
        "text": "A SES-DF reforça que o HRAN é o polo de distribuição de soros para picadas de animais peçonhentos.",
        "source_url": "https://www.saude.df.gov.br/soros",
        "tag": "EMERGENCIA",
    }

    # Sem chave -> 403
    r1 = client.post("/api/ingestion/webhook", json=payload_dict)
    assert r1.status_code == 403

    # Com chave inválida -> 403
    r2 = client.post(
        "/api/ingestion/webhook",
        json=payload_dict,
        headers={"X-Ingestion-Key": "chave-incorreta"},
    )
    assert r2.status_code == 403

    # Com chave válida -> 200
    r3 = client.post(
        "/api/ingestion/webhook",
        json=payload_dict,
        headers={"X-Ingestion-Key": "susana-ingest-secret-2026"},
    )
    assert r3.status_code == 200
    data = r3.json()
    assert data["status"] in ("success", "skipped")
    assert "document_id" in data


def test_ingestion_status_endpoint():
    client = TestClient(app)
    r = client.get("/api/ingestion/status")
    assert r.status_code == 200
    data = r.json()
    assert "total_documents" in data
    assert "storage_path" in data


def test_scraper_cleans_html_and_classifies_tags():
    html = """
    <html>
      <head><title>Campanha de Vacinação DF</title></head>
      <body>
        <nav><a href="/">Home</a></nav>
        <main>
          <h1>Campanha de Vacinação contra a Gripe no DF</h1>
          <p>A vacinação contra a influenza começou em todas as UBSs do Distrito Federal para idosos e crianças.</p>
          <script>console.log("ruido");</script>
        </main>
        <footer>Rodapé governamental</footer>
      </body>
    </html>
    """
    title, text = SUSAutonomousScraper.clean_html(html)
    assert "Vacinação" in title
    assert "influenza começou" in text
    assert "console.log" not in text
    assert "Rodapé governamental" not in text

    tag = classify_tag(title, text)
    assert tag == SUSDataTag.VACINACAO


def test_contracts_reject_unauthorized_external_domain():
    with pytest.raises(ValueError, match="não autorizado para ingestão"):
        RawDocumentPayload(
            title="Página Externa Não Oficial",
            text="Texto de teste com comprimento superior a cinquenta caracteres para validação de domínio.",
            source_url="https://site-malicioso.org/sus",
            tag=SUSDataTag.INSTITUCIONAL,
        )


def test_processor_preserves_existing_chroma_index(tmp_path):
    import numpy as np
    from app.rag.corpus import CorpusBlock
    from app.rag.retriever import ChromaRetriever

    class DummyEmbedder:
        slug = "dummy"
        def encode_passages(self, texts):
            return np.ones((len(texts), 4), dtype=np.float32)

    # 1. Cria retriever com 3 blocos pré-existentes
    retriever = ChromaRetriever(DummyEmbedder(), tmp_path / "chroma_test")
    existing_blocks = [
        CorpusBlock("id1", "[INST] Doc 1", "INSTITUCIONAL", "Conteúdo do documento 1", "https://www.saude.df.gov.br/1"),
        CorpusBlock("id2", "[INST] Doc 2", "INSTITUCIONAL", "Conteúdo do documento 2", "https://www.saude.df.gov.br/2"),
        CorpusBlock("id3", "[INST] Doc 3", "INSTITUCIONAL", "Conteúdo do documento 3", "https://www.saude.df.gov.br/3"),
    ]
    retriever.index(existing_blocks)
    assert retriever.count() == 3

    # 2. Ingestão incremental de 1 novo documento através do IngestionProcessor
    processor = IngestionProcessor(retriever=retriever, storage_dir=tmp_path / "storage")
    payload = RawDocumentPayload(
        title="Documento Novo Ingerido",
        text="A Secretaria de Saúde do Distrito Federal informa novos horários de atendimento das unidades.",
        source_url="https://www.saude.df.gov.br/novo-horario",
        tag=SUSDataTag.INSTITUCIONAL,
    )
    result = processor.process_document(payload)
    assert result.status == "success"
    assert result.chunks_created >= 1

    # 3. REGRESSÃO CRÍTICA (C1): O índice DEVE conter os 3 blocos anteriores + os novos blocos
    assert retriever.count() == 3 + result.chunks_created


def test_processor_replaces_old_chunks_on_url_content_update(tmp_path):
    import numpy as np
    from app.rag.retriever import ChromaRetriever

    class DummyEmbedder:
        slug = "dummy"
        def encode_passages(self, texts):
            return np.ones((len(texts), 4), dtype=np.float32)

    retriever = ChromaRetriever(DummyEmbedder(), tmp_path / "chroma_update_test")
    processor = IngestionProcessor(retriever=retriever, storage_dir=tmp_path / "storage_update")

    # Ingestão 1
    p1 = RawDocumentPayload(
        title="Horários Antigos",
        text="Texto da versão antiga do horário de atendimento da UBS da Ceilândia no Distrito Federal.",
        source_url="https://www.saude.df.gov.br/ubs-horario",
        tag=SUSDataTag.UNIDADE,
    )
    res1 = processor.process_document(p1)
    assert res1.status == "success"
    assert retriever.count() == res1.chunks_created

    # Ingestão 2 com mesma URL mas texto alterado
    p2 = RawDocumentPayload(
        title="Horários Novos Atualizados",
        text="Texto da nova versão atualizada com ampliação do horário de atendimento até as 22h.",
        source_url="https://www.saude.df.gov.br/ubs-horario",
        tag=SUSDataTag.UNIDADE,
    )
    res2 = processor.process_document(p2)
    assert res2.status == "success"
    # Não deve acumular blocos antigos duplicados da mesma URL
    assert retriever.count() == res2.chunks_created
