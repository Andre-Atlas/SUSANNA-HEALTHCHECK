#!/usr/bin/env python3
"""
Benchmark Honesto de Recuperação e Relevância — Susana RAG.
=============================================================
Avalia separadamente partições DEV (calibração) e TEST (conjunto cego congelado),
medindo expressamente:
- Recall@1 e Recall@3 em domínio
- In-Domain Rejected Rate (taxa de falso negativo)
- Out-of-Domain Accepted Rate (taxa de falso positivo / vazamento OOD)
- Latências P50 e P95
- Registro formal no MLflow
"""
from __future__ import annotations

import json
import logging
import statistics
import time
from pathlib import Path
from typing import Any, Dict, List

import mlflow

from app.config import get_settings
from app.rag.corpus import discover_corpus_files, load_corpus
from app.rag.embeddings import Embedder
from app.rag.retriever import ChromaRetriever, is_relevant

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("susana.eval.honest")

BACKEND_DIR = Path(__file__).resolve().parents[2]
EVAL_DIR = BACKEND_DIR / "data" / "eval"


def load_dataset(filename: str) -> List[Dict[str, Any]]:
    path = EVAL_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Arquivo de avaliação não encontrado: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def evaluate_partition(
    retriever: ChromaRetriever,
    embedder: Embedder,
    in_domain_cases: List[Dict[str, Any]],
    ood_cases: List[Dict[str, Any]],
    threshold: float,
    confident_threshold: float,
    partition_name: str,
) -> Dict[str, Any]:
    logger.info("Avaliando partição: %s (%d in-domain, %d OOD)", partition_name, len(in_domain_cases), len(ood_cases))

    # 1. Embeddings em lote
    all_queries = [c["query"] for c in in_domain_cases] + [c["query"] for c in ood_cases]
    vectors = embedder.encode_queries(all_queries)

    # 2. Avaliação In-Domain
    top1_hits = 0
    top3_hits = 0
    in_domain_rejected = 0
    latencies: List[float] = []

    for idx, case in enumerate(in_domain_cases):
        q = case["query"]
        vec = vectors[idx]
        t0 = time.perf_counter()
        results = retriever.search(vec, k=3, query_text=q)
        latencies.append((time.perf_counter() - t0) * 1000)

        # Checagem de relevância (filtragem de borda)
        relevant = is_relevant(results, q, threshold, confident_threshold)
        if not relevant:
            in_domain_rejected += 1

        # Checagem de acurácia de recuperação (palavras-chave esperadas no top)
        expected_keywords = [kw.lower() for kw in case.get("expected_keywords", [])]
        if results:
            top1_text = (results[0].text + " " + results[0].source).lower()
            if any(kw in top1_text for kw in expected_keywords):
                top1_hits += 1

            top3_text = " ".join(r.text + " " + r.source for r in results).lower()
            if any(kw in top3_text for kw in expected_keywords):
                top3_hits += 1

    # 3. Avaliação Out-of-Domain
    ood_start = len(in_domain_cases)
    ood_accepted = 0
    for idx, case in enumerate(ood_cases):
        q = case["query"]
        vec = vectors[ood_start + idx]
        results = retriever.search(vec, k=3, query_text=q)
        if is_relevant(results, q, threshold, confident_threshold):
            ood_accepted += 1
            logger.warning("[%s] OOD VAZOU: '%s' -> Top: %s (dist=%.3f)", partition_name, q, results[0].source, results[0].distance)

    latencies.sort()
    p50 = statistics.median(latencies) if latencies else 0.0
    p95 = latencies[int(len(latencies) * 0.95)] if latencies else 0.0

    n_id = len(in_domain_cases)
    n_ood = len(ood_cases)

    return {
        "partition": partition_name,
        "in_domain_cases": n_id,
        "recall_at_1": round(top1_hits / n_id, 4) if n_id else 0.0,
        "recall_at_3": round(top3_hits / n_id, 4) if n_id else 0.0,
        "in_domain_rejected_count": in_domain_rejected,
        "in_domain_rejected_rate": round(in_domain_rejected / n_id, 4) if n_id else 0.0,
        "ood_cases": n_ood,
        "ood_accepted_count": ood_accepted,
        "ood_accepted_rate": round(ood_accepted / n_ood, 4) if n_ood else 0.0,
        "search_p50_ms": round(p50, 2),
        "search_p95_ms": round(p95, 2),
    }


def main():
    settings = get_settings()
    mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
    mlflow.set_experiment("susana-retrieval-honest-eval")

    logger.info("Carregando datasets de avaliação congelados...")
    id_dev = load_dataset("in_domain_dev.json")
    id_test = load_dataset("in_domain_test.json")
    ood_dev = load_dataset("ood_dev.json")
    ood_test = load_dataset("ood_test.json")

    embedder = Embedder(settings.embedding_model, settings.embedding_max_seq_length)
    corpus_files = discover_corpus_files([settings.docs_dir, settings.project_corpus_dir, settings.legacy_docs_file])
    blocks = load_corpus(corpus_files)
    logger.info("Total de blocos no corpus oficial: %d", len(blocks))

    # Usa o ChromaRetriever em diretório de teste persistido temporário ou o oficial
    retriever = ChromaRetriever(embedder, settings.chroma_dir)
    if retriever.count() == 0:
        retriever.index(blocks)

    logger.info("ChromaDB indexado com %d documentos.", retriever.count())

    with mlflow.start_run(run_name="honest-benchmark-frozen-splits"):
        mlflow.log_params({
            "embedding_model": settings.embedding_model,
            "similarity_threshold": settings.similarity_threshold,
            "confident_threshold": settings.relevance_confident_threshold,
            "total_indexed_blocks": retriever.count(),
        })

        # 1. Avaliação na partição DEV (calibração)
        dev_metrics = evaluate_partition(
            retriever, embedder, id_dev, ood_dev,
            settings.similarity_threshold, settings.relevance_confident_threshold, "DEV"
        )
        for k, v in dev_metrics.items():
            if isinstance(v, (int, float)):
                mlflow.log_metric(f"dev_{k}", v)

        # 2. Avaliação única na partição TEST (cega)
        test_metrics = evaluate_partition(
            retriever, embedder, id_test, ood_test,
            settings.similarity_threshold, settings.relevance_confident_threshold, "TEST"
        )
        for k, v in test_metrics.items():
            if isinstance(v, (int, float)):
                mlflow.log_metric(f"test_{k}", v)

        print("\n" + "="*60)
        print("🎯 RELATÓRIO DO BENCHMARK HONESTO (Fase B)")
        print("="*60)
        print(f"DEV Metrics: Recall@1={dev_metrics['recall_at_1']:.1%}, Recall@3={dev_metrics['recall_at_3']:.1%}, "
              f"FN Rejeição Legítima={dev_metrics['in_domain_rejected_rate']:.1%}, FP Vazamento OOD={dev_metrics['ood_accepted_rate']:.1%}")
        print(f"TEST Metrics: Recall@1={test_metrics['recall_at_1']:.1%}, Recall@3={test_metrics['recall_at_3']:.1%}, "
              f"FN Rejeição Legítima={test_metrics['in_domain_rejected_rate']:.1%}, FP Vazamento OOD={test_metrics['ood_accepted_rate']:.1%}")
        print(f"Latências P50={test_metrics['search_p50_ms']}ms | P95={test_metrics['search_p95_ms']}ms")
        print("="*60 + "\n")

        # Portão Bloqueante de Qualidade (Fase B)
        assert test_metrics["ood_accepted_rate"] <= 0.05, f"Vazamento OOD excessivo no TEST: {test_metrics['ood_accepted_rate']:.1%}"
        assert test_metrics["in_domain_rejected_rate"] <= 0.10, f"Falso negativo excessivo no TEST: {test_metrics['in_domain_rejected_rate']:.1%}"
        assert test_metrics["recall_at_3"] >= 0.85, f"Recall@3 insuficiente no TEST: {test_metrics['recall_at_3']:.1%}"
        print("✅ Portão de Avaliação Honesta APROVADO com sucesso!")


if __name__ == "__main__":
    main()
