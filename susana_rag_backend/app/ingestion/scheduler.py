"""Agendador e executor autônomo para ciclo contínuo de scraping e ingestão do SUS."""
from __future__ import annotations

import argparse
import asyncio
import logging
from pathlib import Path
from typing import List

import yaml

from app.config import get_settings
from app.ingestion.processor import IngestionProcessor
from app.ingestion.scraper import SUSAutonomousScraper
from app.rag.embeddings import Embedder
from app.rag.retriever import ChromaRetriever

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("susana.ingestion.scheduler")


def load_seed_urls() -> List[str]:
    """Carrega URLs sementes do sources.yaml existente."""
    sources_file = Path(__file__).resolve().parents[2] / "ml" / "corpus" / "sources.yaml"
    urls = []
    if sources_file.exists():
        try:
            data = yaml.safe_load(sources_file.read_text(encoding="utf-8")) or {}
            urls = [s.get("url") for s in data.get("sources", []) if s.get("url")]
        except Exception as e:
            logger.warning("Falha ao carregar sources.yaml: %s", e)
    
    # Sementes padrão caso sources.yaml esteja vazio
    if not urls:
        urls = [
            "https://www.saude.df.gov.br",
            "https://www.saude.df.gov.br/vacinacao",
            "https://www.saude.df.gov.br/samu",
            "https://www.saude.df.gov.br/farmacia-alto-custo",
        ]
    return urls


async def run_ingestion_cycle(limit_urls: int = 15) -> None:
    settings = get_settings()
    logger.info("Iniciando ciclo autônomo de coleta do ecossistema SUS...")

    # 1. Conexão ao ChromaDB para indexação dinâmica
    embedder = Embedder(settings.embedding_model, settings.embedding_max_seq_length)
    retriever = ChromaRetriever(embedder, settings.chroma_dir)
    processor = IngestionProcessor(retriever=retriever)

    # 2. Coleta ativa de dados
    seeds = load_seed_urls()[:limit_urls]
    scraper = SUSAutonomousScraper(delay_seconds=0.8)
    documents = await scraper.run_discovery_crawl(seeds)

    # 3. Processamento e indexação incremental
    success_count = 0
    duplicate_count = 0
    for doc in documents:
        res = processor.process_document(doc)
        if res.status == "success":
            success_count += 1
        elif res.is_duplicate:
            duplicate_count += 1

    logger.info(
        "Ciclo de ingestão concluído: %d novos indexados, %d duplicados ignorados. Total no índice: %d",
        success_count,
        duplicate_count,
        retriever.count(),
    )


def main():
    parser = argparse.ArgumentParser(description="Ciclo autônomo de coleta e ingestão SUS")
    parser.add_argument("--limit", type=int, default=10, help="Limite de URLs para varredura")
    args = parser.parse_args()
    asyncio.run(run_ingestion_cycle(limit_urls=args.limit))


if __name__ == "__main__":
    main()
