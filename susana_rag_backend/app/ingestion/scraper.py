"""Scraper autônomo e assíncrono para o ecossistema SUS (SES-DF, CKAN e Ministério da Saúde)."""
from __future__ import annotations

import asyncio
import logging
import re
from datetime import datetime, timezone
from typing import AsyncIterator, List, Optional
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

from app.ingestion.contracts import RawDocumentPayload, SUSDataTag

logger = logging.getLogger("susana.ingestion.scraper")

USER_AGENT = "SusanaAutonomousIngestionBot/1.0 (+https://saude.df.gov.br; assistente institucional)"
DEFAULT_TIMEOUT = 12.0
MIN_TEXT_CHARS = 100
MAX_PAGE_CHARS = 15000

NOISE_SELECTORS = [
    "script", "style", "noscript", "nav", "footer", "header", "aside",
    "form", "iframe", "svg", "button", ".menu", ".breadcrumb", ".social",
    ".share", "[role=navigation]", ".lfr-nav", ".skip-link", ".footer",
]

MAIN_CONTENT_SELECTORS = [
    ".journal-content-article", "#main-content", "#content", "article",
    "main", "[role=main]", ".conteudo-principal", ".page-content"
]


def classify_tag(title: str, text: str) -> SUSDataTag:
    """Classifica a tag semântica do SUS baseada no léxico do título e texto."""
    combined = f"{title} {text}".lower()
    if any(k in combined for k in ["vacina", "imunização", "dose", "campanha vacinal", "sarampo", "gripe"]):
        return SUSDataTag.VACINACAO
    if any(k in combined for k in ["samu", "192", "emergência", "urgência", "pronto-socorro"]):
        return SUSDataTag.EMERGENCIA
    if any(k in combined for k in ["remédio", "medicamento", "farmácia", "insulina", "ceaf", "reme"]):
        return SUSDataTag.MEDICAMENTO
    if any(k in combined for k in ["hospital", "ubs", "upa", "policlínica", "unidade básica", "caps"]):
        return SUSDataTag.UNIDADE
    if any(k in combined for k in ["dengue", "epidemia", "boletim", "casos", "chikungunya", "zika", "óbito"]):
        return SUSDataTag.EPIDEMIOLOGIA
    if any(k in combined for k in ["agendamento", "sisreg", "consulta", "exame", "cartão sus"]):
        return SUSDataTag.SERVICO
    return SUSDataTag.INSTITUCIONAL


class SUSAutonomousScraper:
    """Scraper com coleta respeitosa, sanitização e extração semântica."""

    def __init__(self, delay_seconds: float = 1.0, timeout_seconds: float = DEFAULT_TIMEOUT):
        self.delay_seconds = delay_seconds
        self.timeout = timeout_seconds
        self.headers = {"User-Agent": USER_AGENT}

    @staticmethod
    def clean_html(html: str) -> Tuple[str, str]:
        """Extrai título e texto limpo do HTML."""
        soup = BeautifulSoup(html, "html.parser")
        
        # 1. Título
        title = ""
        if soup.title and soup.title.string:
            title = soup.title.string.strip()
        h1 = soup.find("h1")
        if h1 and h1.get_text(strip=True):
            title = h1.get_text(strip=True)
        if not title:
            title = "Documento Informativo SUS-DF"

        # 2. Remoção de elementos ruidosos
        for sel in NOISE_SELECTORS:
            for el in soup.select(sel):
                el.decompose()

        # 3. Localização da área de conteúdo principal
        main_root = None
        for sel in MAIN_CONTENT_SELECTORS:
            cands = soup.select(sel)
            if cands:
                main_root = max(cands, key=lambda c: len(c.get_text(strip=True)))
                break
        main_root = main_root or soup.body or soup

        # 4. Agrupamento de parágrafos legíveis
        paragraphs = []
        for p in main_root.find_all(["p", "li", "h2", "h3", "h4", "td"]):
            text = re.sub(r"\s+", " ", p.get_text(strip=True)).strip()
            if len(text) >= 30:
                paragraphs.append(text)

        cleaned_text = "\n\n".join(paragraphs)[:MAX_PAGE_CHARS]
        return title, cleaned_text

    async def fetch_url(self, client: httpx.AsyncClient, url: str) -> Optional[RawDocumentPayload]:
        try:
            resp = await client.get(url, headers=self.headers, timeout=self.timeout, follow_redirects=True)
            if resp.status_code != 200:
                logger.warning("Falha HTTP %d ao coletar %s", resp.status_code, url)
                return None
            
            title, text = self.clean_html(resp.text)
            if len(text) < MIN_TEXT_CHARS:
                logger.debug("Texto insuficiente (<%d chars) em %s", MIN_TEXT_CHARS, url)
                return None

            tag = classify_tag(title, text)
            return RawDocumentPayload(
                title=title[:280],
                text=text,
                source_url=url,
                tag=tag,
                author_or_department="SES-DF / Ministério da Saúde",
                fetched_at=datetime.now(timezone.utc),
            )
        except Exception as e:
            logger.warning("Exceção ao coletar URL %s: %s", url, e)
            return None

    async def crawl_ckan_opendata(self, client: httpx.AsyncClient, query: str = "saude", max_rows: int = 25) -> List[RawDocumentPayload]:
        """Consulta dinamicamente o catálogo CKAN de Dados Abertos do DF."""
        ckan_api = "https://dados.df.gov.br/api/3/action/package_search"
        payloads: List[RawDocumentPayload] = []
        try:
            resp = await client.get(ckan_api, params={"q": query, "rows": max_rows}, headers=self.headers, timeout=self.timeout)
            if resp.status_code != 200:
                return []
            data = resp.json()
            packages = data.get("result", {}).get("results", [])
            for pkg in packages:
                title = pkg.get("title", "")
                notes = pkg.get("notes", "") or ""
                # Limpa tags HTML das notas do CKAN
                soup = BeautifulSoup(notes, "html.parser")
                clean_notes = soup.get_text(" ", strip=True)
                name = pkg.get("name", "")
                url = f"https://dados.df.gov.br/dataset/{name}" if name else ckan_api
                
                if len(clean_notes) >= MIN_TEXT_CHARS:
                    tag = classify_tag(title, clean_notes)
                    payloads.append(
                        RawDocumentPayload(
                            title=f"Dados Abertos: {title}"[:280],
                            text=clean_notes,
                            source_url=url,
                            tag=tag,
                            author_or_department="Portal de Dados Abertos do DF",
                        )
                    )
        except Exception as e:
            logger.warning("Falha ao coletar CKAN dados.df.gov.br: %s", e)
        return payloads

    async def run_discovery_crawl(self, seed_urls: List[str]) -> List[RawDocumentPayload]:
        """Executa a descoberta assíncrona sobre as sementes fornecidas."""
        results: List[RawDocumentPayload] = []
        async with httpx.AsyncClient(verify=True) as client:
            # 1. Coleta CKAN
            ckan_items = await self.crawl_ckan_opendata(client)
            results.extend(ckan_items)

            # 2. Coleta de páginas web
            for url in seed_urls:
                doc = await self.fetch_url(client, url)
                if doc:
                    results.append(doc)
                await asyncio.sleep(self.delay_seconds)

        logger.info("Coleta autônoma finalizada: %d documentos brutos extraídos.", len(results))
        return results
