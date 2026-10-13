"""
Sincronizador e Re-indexador do Corpus no ChromaDB.
Carrega todos os arquivos de dados (incluindo o novo diretório das 33 RAs do DF),
extrai os metadados enriquecidos (cluster, ra, tipo_unidade, servicos) e realiza o upsert no ChromaDB.
"""
from __future__ import annotations

import logging
import time
from pathlib import Path

from app.config import get_settings
from app.rag.corpus import discover_corpus_files, load_corpus
from app.rag.embeddings import Embedder
from app.rag.retriever import ChromaRetriever

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("susana.sync_chroma")


def sync_chroma():
    settings = get_settings()
    logger.info("Iniciando sincronização de corpus no ChromaDB (%s)...", settings.chroma_dir)

    roots = [settings.docs_dir, settings.project_corpus_dir, settings.legacy_docs_file]
    files = discover_corpus_files(roots)
    logger.info("Arquivos de corpus descobertos (%d): %s", len(files), [f.name for f in files])

    t0 = time.perf_counter()
    blocks = load_corpus(files)
    logger.info("Total de blocos carregados e enriquecidos: %d em %.2fs", len(blocks), time.perf_counter() - t0)

    embedder = Embedder(settings.embedding_model, settings.embedding_max_seq_length)
    retriever = ChromaRetriever(embedder, settings.chroma_dir)

    initial_count = retriever.count()
    logger.info("Contagem atual de blocos no ChromaDB: %d", initial_count)

    t_upsert = time.perf_counter()
    total_synced = retriever.upsert(blocks, batch_size=128)
    final_count = retriever.count()
    logger.info(
        "Sincronização concluída em %.2fs! %d blocos processados. Total final no ChromaDB: %d",
        time.perf_counter() - t_upsert,
        total_synced,
        final_count,
    )


if __name__ == "__main__":
    sync_chroma()
