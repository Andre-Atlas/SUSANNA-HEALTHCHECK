#!/usr/bin/env python3
"""
Fase 2: Benchmark de Modelos de Embedding
Avalia modelos de embedding usando o dataset de validação (eval_set.jsonl).
Registra métricas (Hit Rate no Top-3) no MLflow.
"""
import json
import logging
import os
from pathlib import Path

import mlflow
from sentence_transformers import SentenceTransformer

from app.config import get_settings
from app.rag.embeddings import Embedder
from app.rag.retriever import ChromaRetriever

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger("susana.ml.benchmark")

ROOT = Path(__file__).resolve().parent.parent.parent
EVAL_FILE = ROOT / "ml" / "retrieval" / "eval_set.jsonl"
CORPUS_FILE = ROOT / "data" / "corpus" / "sesdf_public.txt"

CANDIDATES = [
    "all-MiniLM-L6-v2",
    "paraphrase-multilingual-MiniLM-L12-v2",
]


def load_eval_set():
    data = []
    with open(EVAL_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))
    return data


def main():
    settings = get_settings()
    os.makedirs(settings.mlflow_artifact_root, exist_ok=True)
    mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
    mlflow.set_experiment("susana-embeddings-benchmark")

    eval_data = load_eval_set()
    from app.rag.corpus import load_corpus
    blocks = load_corpus([CORPUS_FILE])
    
    if not blocks:
        logger.error("Corpus vazio ou não encontrado em %s", CORPUS_FILE)
        return

    best_model = None
    best_score = -1.0

    for model_name in CANDIDATES:
        with mlflow.start_run(run_name=f"benchmark_{model_name}"):
            logger.info("Testando modelo: %s", model_name)
            mlflow.log_param("model", model_name)

            embedder = Embedder(model_name)
            retriever = ChromaRetriever(embedder, settings.chroma_dir, collection_prefix="bench")
            
            # Limpar coleção antiga do benchmark (se existir) para forçar re-indexação isolada?
            # O ChromaRetriever usa collection baseada no nome do modelo, então não colide.
            
            indexed = retriever.index(blocks)
            logger.info("Indexados %d blocos usando %s", indexed, model_name)

            hits = 0
            for item in eval_data:
                q = item["query"]
                expected_tag = item["expected_tag"]
                
                vec = embedder.encode_queries([q])[0]
                results = retriever.search(vec, k=3)
                
                # Check if expected_tag is in any of the top 3 results' tags or sources
                # We stored tag in metadata. For standard search we appended to source.
                found = False
                for r in results:
                    # Our ChromaRetriever currently sets source = meta.get("source") + url
                    # In parse_corpus_text, source is the header: [UNIDADE] UBS ...
                    if f"[{expected_tag}]" in r.source:
                        found = True
                        break
                if found:
                    hits += 1

            hit_rate = hits / len(eval_data) if eval_data else 0.0
            logger.info("Modelo %s -> Hit Rate (Top-3): %.2f", model_name, hit_rate)
            mlflow.log_metric("hit_rate_top3", hit_rate)

            if hit_rate > best_score:
                best_score = hit_rate
                best_model = model_name

    logger.info("Melhor modelo: %s com Hit Rate de %.2f", best_model, best_score)
    print(f"BENCHMARK_WINNER={best_model}")


if __name__ == "__main__":
    main()
