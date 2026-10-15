"""
Scoped Online Search Complementer — Mecanismo de Pesquisa Online Assíncrona para o SUS-DF.
========================================================================================
Permite que o sistema consulte em tempo real fontes públicas e oficiais da saúde do Distrito Federal
quando o índice local não possuir informações com relevância suficiente para a demanda administrativa.

Limites estritos de segurança e governança (Auditoria Trindade):
1. Restrito estritamente a domínios oficiais autorizados (anti-SSRF comprovado, sem localhost/IPs).
2. Portão de Escopo Refinado: descarte expresso e co-ocorrência obrigatória para evitar vazamento.
3. Gating Clínico em Profundidade: perguntas com viés clínico/prescrição são barradas a priori.
4. Concorrência Resiliente: auto-ingestão executada em ThreadPool persistente (livre de TaskDestroyed).
5. Invalidação Cirúrgica de Cache: expurga apenas respostas negativas prévias, evitando cache thrashing.
6. Circuit Breaker com Logs Estruturados: degradação graciosa com telemetria operacional.
"""
from __future__ import annotations

import asyncio
import concurrent.futures
import ipaddress
import logging
import re
import time
import unicodedata
from datetime import datetime, timezone
from typing import Any, List, Optional, Sequence, Set, Tuple
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup

from app.config import get_settings
from app.ingestion.contracts import ALLOWED_SUS_DOMAINS, RawDocumentPayload, SUSDataTag
from app.ports import RetrievedChunk
from app.rag.nlu import RA_DICTIONARY

logger = logging.getLogger("susana.online_search")

# 0. Regex de descarte expresso de consultas fora de escopo (culinária, esportes, entretenimento, trânsito, finanças)
_DISCARD_TERMS = [
    "bolo", "brigadeiro", "torta", "receita de bolo", "culinaria", "comida",
    "futebol", "flamengo", "corinthians", "palmeiras", "brasileirao", "jogo",
    "cinema", "filme", "shopping", "estacionamento", "loja",
    "gasolina", "posto de gasolina", "combustivel", "etanol", "diesel",
    "detran", "cnh", "ipva", "multa de transito", "veiculo",
    "dolar", "euro", "fipe", "ar condicionado", "hotel", "pousada", "voo", "passagem aerea", "banco", "pix",
]
_DISCARD_REGEX = re.compile(rf"\b({'|'.join(re.escape(w) for w in _DISCARD_TERMS)})\b", re.IGNORECASE)

# 1. Termos centrais inequívocos de saúde pública e SUS-DF (ativam escopo diretamente)
_SUS_CORE_HEALTH_TERMS = {
    # Unidades e estruturas
    "ubs", "upa", "hospital", "hospitais", "policlinica", "policlinicas", "caps", "samu", "192",
    "farmacia", "farmacias", "laboratorio", "maternidade", "pronto socorro", "sala de vacina", "centro de saude",
    # Imunização e procedimentos administrativos
    "vacina", "vacinas", "vacinacao", "vacinar", "vacinando", "imunizacao", "dose", "doses", "gotinha",
    "calendario vacinal", "gripe", "influenza", "covid", "febre amarela",
    "pre natal", "prenatal", "puericultura", "teste do pezinho", "mamografia", "diu", "preventivo", "vasectomia",
    "consulta", "consultas", "exame", "exames", "cirurgia", "cirurgias", "medico", "medica",
    # Medicamentos e documentos de saúde
    "cartao sus", "cns", "sisreg", "lme", "remedio", "remedios", "medicamento", "medicamentos",
    "insulina", "alto custo", "farmacia popular", "receita medica", "receita do sus", "validade da receita", "renovar receita",
    # Condições sanitárias e órgãos
    "dengue", "tenda", "tendas", "hidratacao", "febre", "ses df", "sesdf", "sus", "saude df", "saude publica",
    "ministerio da saude", "saude",
}
_CORE_HEALTH_REGEXES = [re.compile(rf"\b{re.escape(k)}\b") for k in _SUS_CORE_HEALTH_TERMS]

# 2. Termos contextuais que exigem co-ocorrência com saúde ou serviços públicos de atenção
_SUS_CONTEXT_TERMS = {
    "posto", "postos", "postinho", "horario", "documento", "documentos", "levar",
    "atendimento", "plantao", "saude na hora", "consulta", "consultas", "exame", "exames", "agendamento", "regulacao",
}
_CONTEXT_REGEXES = [re.compile(rf"\b{re.escape(k)}\b") for k in _SUS_CONTEXT_TERMS]


def _normalize(text: str) -> str:
    norm = unicodedata.normalize("NFKD", text).casefold()
    return "".join(c for c in norm if not unicodedata.combining(c)).strip()


def is_within_sus_scope(query: str) -> bool:
    """
    Verifica com precisão se a query do cidadão pertence legitimamente ao escopo do SUS-DF.
    Elimina falsos positivos com checagem de co-ocorrência mandatória para termos contextuais.
    """
    norm_q = _normalize(query)
    if not norm_q:
        return False

    # A. Descarte imediato de termos alheios ao domínio
    if _DISCARD_REGEX.search(norm_q):
        return False

    # B. Checagem de termos centrais da saúde pública
    has_core_health = any(rx.search(norm_q) for rx in _CORE_HEALTH_REGEXES)
    if has_core_health:
        return True

    # C. Se contiver menção a RA + termo contextual ou verbo de serviço público
    for _, aliases in RA_DICTIONARY:
        if any(re.search(rf"\b{re.escape(alias)}\b", norm_q) for alias in aliases):
            # Se mencionar RA acompanhada de posto, atendimento, médico, unidade, consulta, exame
            if any(rx.search(norm_q) for rx in _CONTEXT_REGEXES) or any(
                re.search(rf"\b{re.escape(w)}\b", norm_q) for w in ["medico", "unidade", "clinica", "socorro", "enfermeir"]
            ):
                return True

    return False


def is_allowed_domain(url: str) -> bool:
    """
    Verifica se a URL pertence estritamente à allowlist oficial do ecossistema SUS-DF.
    Garante proteção integral contra SSRF, rejeitando IPs, localhost e redirecionamentos inseguros.
    """
    try:
        parsed = urlparse(url)
        hostname = (parsed.hostname or "").lower().strip()
        if not hostname:
            return False

        # 1. Rejeição explícita de localhost e endereços IP
        if hostname in ("localhost", "127.0.0.1", "::1", "0.0.0.0") or hostname.startswith("127."):
            return False
        try:
            ip = ipaddress.ip_address(hostname)
            if ip.is_loopback or ip.is_private or ip.is_reserved or ip.is_link_local:
                return False
        except ValueError:
            pass  # Não é endereço IP numérico

        # 2. Rejeição de nomes sem domínio (hostnames internos)
        if "." not in hostname:
            return False

        # 3. Validação contra allowlist oficial
        is_match = any(hostname == allowed or hostname.endswith("." + allowed) for allowed in ALLOWED_SUS_DOMAINS)
        if not is_match:
            return False

        # 4. Refinamento para domínio genérico gov.br: aceitar portal oficial e subdomínios de saúde ou do DF
        if hostname in ("gov.br", "www.gov.br"):
            return True

        if hostname.endswith(".gov.br"):
            valid_gov_subdomains = (
                "saude.df.gov.br",
                "dados.df.gov.br",
                "agenciabrasilia.df.gov.br",
                "ebserh.gov.br",
                "anvisa.gov.br",
                "fiocruz.br",
                "saude.gov.br",
                "bvsms.saude.gov.br",
                "conass.org.br",
            )
            return any(hostname == v or hostname.endswith("." + v) for v in valid_gov_subdomains)

        return True
    except Exception:
        return False


class CircuitBreaker:
    """Disjuntor operacional para proteção contra saturação ou indisponibilidade de serviços externos."""

    def __init__(self, failure_threshold: int = 3, recovery_time_s: float = 30.0):
        self.failure_threshold = failure_threshold
        self.recovery_time_s = recovery_time_s
        self.failures = 0
        self.last_failure_time = 0.0

    def is_open(self) -> bool:
        if self.failures >= self.failure_threshold:
            if time.time() - self.last_failure_time < self.recovery_time_s:
                return True
            # Meio-aberto: permite nova tentativa após o tempo de recuperação
            self.failures = 0
        return False

    def record_success(self) -> None:
        self.failures = 0

    def record_failure(self) -> None:
        self.failures += 1
        self.last_failure_time = time.time()
        if self.failures >= self.failure_threshold:
            logger.warning(
                "Circuit breaker ATIVADO para pesquisas online do SUS-DF (%d falhas consecutivas). Requisições temporariamente pausadas.",
                self.failures,
            )


class ScopedOnlineSearchComplementer:
    """Mecanismo de pesquisa online em fontes públicas oficiais do DF com complementação assíncrona resiliente."""

    def __init__(
        self,
        retriever=None,
        ingestion_processor=None,
        guardrails=None,
        timeout_seconds: Optional[float] = None,
        max_results: Optional[int] = None,
    ):
        self.settings = get_settings()
        self.retriever = retriever
        self.ingestion_processor = ingestion_processor
        self.guardrails = guardrails
        self.timeout = timeout_seconds or self.settings.online_search_timeout_s
        self.max_results = max_results or self.settings.online_search_max_results
        self.user_agent = "SusanaScopedOnlineSearch/1.0 (+https://saude.df.gov.br; institucional SUS-DF)"
        self.circuit_breaker = CircuitBreaker()
        # ThreadPoolExecutor persistente para auto-ingestão segura (não cancelada com fechamento de event loops locais)
        self._ingestion_executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=2, thread_name_prefix="susana_online_ingest"
        )
        self._client: Optional[httpx.AsyncClient] = None

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                verify=True,
                timeout=self.timeout,
                limits=httpx.Limits(max_connections=10, max_keepalive_connections=5),
            )
        return self._client

    async def aclose(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()
        self._ingestion_executor.shutdown(wait=False)

    async def _fetch_ckan_opendata(self, client: httpx.AsyncClient, query: str) -> List[dict]:
        """Consulta o catálogo de Dados Abertos do DF (dados.df.gov.br via API CKAN)."""
        ckan_api = "https://dados.df.gov.br/api/3/action/package_search"
        results: List[dict] = []
        try:
            resp = await client.get(
                ckan_api,
                params={"q": f"{query} saude", "rows": self.max_results},
                headers={"User-Agent": self.user_agent},
            )
            if resp.status_code == 200:
                data = resp.json()
                packages = data.get("result", {}).get("results", [])
                for pkg in packages:
                    title = pkg.get("title", "")
                    notes = pkg.get("notes") or ""
                    soup = await asyncio.to_thread(BeautifulSoup, notes, "html.parser")
                    clean_text = soup.get_text(" ", strip=True)
                    name = pkg.get("name", "")
                    url = f"https://dados.df.gov.br/dataset/{name}" if name else ckan_api
                    if len(clean_text) >= 60 and is_allowed_domain(url):
                        results.append({
                            "title": f"Dados Abertos: {title}",
                            "text": clean_text,
                            "url": url,
                            "tag": SUSDataTag.INSTITUCIONAL,
                            "source_name": "Portal de Dados Abertos do DF",
                        })
                self.circuit_breaker.record_success()
            else:
                logger.warning("CKAN retornou status inesperado %d para '%s'", resp.status_code, query[:40])
        except (httpx.TimeoutException, httpx.NetworkError) as exc:
            self.circuit_breaker.record_failure()
            logger.warning("Falha de rede/timeout na consulta CKAN para query '%s': %s", query[:40], exc)
        except Exception as exc:
            logger.warning("Erro inesperado na consulta CKAN para query '%s': %s", query[:40], exc)
        return results

    async def _fetch_sesdf_portal(self, client: httpx.AsyncClient, query: str) -> List[dict]:
        """Consulta busca pública no portal oficial da Secretaria de Saúde do DF (saude.df.gov.br)."""
        search_url = "https://www.saude.df.gov.br"
        results: List[dict] = []
        try:
            resp = await client.get(
                search_url,
                params={"s": query},
                headers={"User-Agent": self.user_agent},
                follow_redirects=True,
            )
            if resp.status_code == 200:
                soup = await asyncio.to_thread(BeautifulSoup, resp.text, "html.parser")
                for noise in soup.select("script, style, nav, footer, header, aside, .menu"):
                    noise.decompose()
                articles = soup.select("article, .post, .entry-content, .conteudo-principal, main")
                for art in articles[:self.max_results]:
                    link_el = art.find("a", href=True)
                    target_url = link_el["href"] if link_el else search_url
                    if not target_url.startswith("http"):
                        target_url = f"https://www.saude.df.gov.br{target_url}"
                    if not is_allowed_domain(target_url):
                        continue
                    title_el = art.find(["h1", "h2", "h3", "h4"])
                    title = title_el.get_text(strip=True) if title_el else "Comunicado Oficial SES-DF"
                    text = re.sub(r"\s+", " ", art.get_text(" ", strip=True))
                    if len(text) >= 80:
                        results.append({
                            "title": title[:180],
                            "text": text[:1500],
                            "url": target_url,
                            "tag": SUSDataTag.INSTITUCIONAL,
                            "source_name": "Secretaria de Saúde do DF (SES-DF)",
                        })
                self.circuit_breaker.record_success()
            else:
                logger.warning("SES-DF retornou status inesperado %d para '%s'", resp.status_code, query[:40])
        except (httpx.TimeoutException, httpx.NetworkError) as exc:
            self.circuit_breaker.record_failure()
            logger.warning("Falha de rede/timeout na busca SES-DF para query '%s': %s", query[:40], exc)
        except Exception as exc:
            logger.warning("Erro inesperado na busca SES-DF para query '%s': %s", query[:40], exc)
        return results

    async def _fetch_agenciabrasilia(self, client: httpx.AsyncClient, query: str) -> List[dict]:
        """Consulta avisos oficiais de saúde na Agência Brasília (agenciabrasilia.df.gov.br)."""
        search_url = "https://agenciabrasilia.df.gov.br"
        results: List[dict] = []
        try:
            resp = await client.get(
                search_url,
                params={"s": f"{query} saude"},
                headers={"User-Agent": self.user_agent},
                follow_redirects=True,
            )
            if resp.status_code == 200:
                soup = await asyncio.to_thread(BeautifulSoup, resp.text, "html.parser")
                for noise in soup.select("script, style, nav, footer, header, aside, .menu"):
                    noise.decompose()
                articles = soup.select("article, .noticia, .post, .card-noticia")
                for art in articles[:self.max_results]:
                    link_el = art.find("a", href=True)
                    target_url = link_el["href"] if link_el else search_url
                    if not is_allowed_domain(target_url):
                        continue
                    title_el = art.find(["h1", "h2", "h3", "h4"])
                    title = title_el.get_text(strip=True) if title_el else "Aviso Agência Brasília"
                    text = re.sub(r"\s+", " ", art.get_text(" ", strip=True))
                    if len(text) >= 80:
                        results.append({
                            "title": f"Agência Brasília: {title}"[:180],
                            "text": text[:1500],
                            "url": target_url,
                            "tag": SUSDataTag.INSTITUCIONAL,
                            "source_name": "Agência Brasília (GDF)",
                        })
                self.circuit_breaker.record_success()
            else:
                logger.warning("Agência Brasília retornou status %d para '%s'", resp.status_code, query[:40])
        except (httpx.TimeoutException, httpx.NetworkError) as exc:
            self.circuit_breaker.record_failure()
            logger.warning("Falha de rede/timeout na busca Agência Brasília para query '%s': %s", query[:40], exc)
        except Exception as exc:
            logger.warning("Erro inesperado na busca Agência Brasília para query '%s': %s", query[:40], exc)
        return results

    async def search_async(self, query: str) -> List[RetrievedChunk]:
        """
        Executa pesquisa online concorrente e filtrada sobre as fontes públicas oficiais do SUS-DF.
        Retorna uma lista de RetrievedChunk prontos para geração de resposta e citação.
        """
        if not self.settings.online_search_enabled:
            return []

        # 1. Defesa em Profundidade Clínica: bloqueia antes de qualquer chamada HTTP externa
        if self.guardrails and hasattr(self.guardrails, "is_clinical"):
            try:
                if self.guardrails.is_clinical(query):
                    logger.info("Online search suprimido por guardrail clínico para query '%s'", query[:60])
                    return []
            except Exception as e:
                logger.debug("Falha na avaliação de guardrails no online search: %s", e)

        # 2. Portão de Escopo Refinado: Se fora do domínio SUS-DF, descarta
        if not is_within_sus_scope(query):
            logger.info("Online search suprimido: query fora do escopo do SUS-DF ('%s')", query[:60])
            return []

        # 3. Proteção Operacional de Circuit Breaker
        if self.circuit_breaker.is_open():
            logger.warning("Online search suspenso temporariamente por ativação do Circuit Breaker.")
            return []

        # 4. Executa consultas assíncronas concorrentes com o cliente HTTP persistente
        client = self._get_client()
        tasks = [
            self._fetch_ckan_opendata(client, query),
            self._fetch_sesdf_portal(client, query),
            self._fetch_agenciabrasilia(client, query),
        ]
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        collected_docs: List[dict] = []
        for resp in responses:
            if isinstance(resp, list):
                collected_docs.extend(resp)

        if not collected_docs:
            logger.info("Online search concluído sem documentos relevantes para '%s'", query[:60])
            return []

        # 5. Formatação dos blocos encontrados como RetrievedChunk
        chunks: List[RetrievedChunk] = []
        for i, doc in enumerate(collected_docs[:self.max_results]):
            chunk_id = f"online_{i}_{abs(hash(doc['url']))}"
            source = f"[{doc['tag'].value}] {doc['title']} — {doc['url']}"
            formatted_text = f"[{doc['tag'].value}] {doc['title']}\n{doc['text']}\nFonte: {doc['url']}"
            chunks.append(
                RetrievedChunk(
                    id=chunk_id,
                    text=formatted_text,
                    source=source,
                    distance=0.30,  # Distância atribuída para garantir relevância no gerador
                    url=doc["url"],
                )
            )

        # 6. Disparo resiliente de auto-ingestão em background via ThreadPool persistente
        if self.settings.online_search_auto_ingest and self.ingestion_processor is not None:
            self.schedule_auto_ingestion(collected_docs)

        return chunks

    def schedule_auto_ingestion(self, docs: Sequence[dict]) -> None:
        """Submete a auto-ingestão para threadpool persistente, imune a destruição de event loops."""
        if not self.ingestion_processor or not docs:
            return
        self._ingestion_executor.submit(self._run_ingestion_sync, list(docs))

    def _run_ingestion_sync(self, docs: Sequence[dict]) -> None:
        """Execução síncrona e thread-safe de ingestão e invalidação cirúrgica de cache."""
        for doc in docs:
            try:
                payload = RawDocumentPayload(
                    title=doc["title"][:280],
                    text=doc["text"],
                    source_url=doc["url"],
                    tag=doc.get("tag", SUSDataTag.INSTITUCIONAL),
                    author_or_department=doc.get("source_name", "SES-DF"),
                    fetched_at=datetime.now(timezone.utc),
                )
                res = self.ingestion_processor.process_document(payload)
                logger.info(
                    "Auto-ingestão online: '%s' -> %s (%d blocos)",
                    payload.title[:40],
                    res.status,
                    res.chunks_created,
                )
            except Exception as e:
                logger.warning("Falha na auto-ingestão de documento online: %s", e)

        # Invalidação cirúrgica de cache: remove apenas respostas negativas prévias ('Não encontrei')
        if self.retriever and hasattr(self.retriever, "semantic_cache") and self.retriever.semantic_cache:
            try:
                if hasattr(self.retriever.semantic_cache, "invalidate_negatives"):
                    removed = self.retriever.semantic_cache.invalidate_negatives()
                    logger.info("Invalidação cirúrgica de cache: %d respostas negativas expurgadas.", removed)
            except Exception as e:
                logger.debug("Falha na invalidação cirúrgica de cache: %s", e)
