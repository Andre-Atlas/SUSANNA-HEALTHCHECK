#!/usr/bin/env python3
"""
Calibração do limiar de relevância (SIMILARITY_THRESHOLD).

Para cada pergunta de ml/retrieval/threshold_set.jsonl (marcada como dentro ou fora do
tema), roda a MESMA busca de produção (híbrida, num índice Chroma temporário) e mede a
menor distância entre os k trechos; a aceitação usa `is_relevant` (que inclui a exceção por
entidade numerada). Escolhe o limiar que separa melhor os dois grupos, priorizando NÃO
recusar perguntas do tema.

Critério: entre os limiares que aceitam MIN_IN_DOMAIN_ACCEPTED (100%) das perguntas do tema,
escolhe o que recusa mais perguntas fora do tema. Registra no MLflow.

Uso: python -m ml.retrieval.calibrate_threshold
"""
import json
import logging
import os
from pathlib import Path

import mlflow
import numpy as np

from app.config import get_settings
from app.rag.corpus import discover_corpus_files, load_corpus
from app.rag.embeddings import Embedder
from app.rag.retriever import ChromaRetriever, is_relevant
from app.rag.glossary import expand_acronyms

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger("susana.ml.calibrate")

ROOT = Path(__file__).resolve().parent.parent.parent
EVAL_FILE = ROOT / "ml" / "retrieval" / "threshold_set.jsonl"
MIN_IN_DOMAIN_ACCEPTED = 1.0  # recusar pergunta válida é pior que deixar o prompt recusar uma fora do tema


def main() -> int:
    settings = get_settings()
    items = [json.loads(line) for line in EVAL_FILE.read_text(encoding="utf-8").splitlines() if line.strip()]
    blocks = load_corpus(discover_corpus_files(settings.corpus_roots))
    if not blocks:
        logger.error("Corpus vazio em %s", settings.docs_dir)
        return 1

    embedder = Embedder(settings.embedding_model, settings.embedding_max_seq_length)
    # Índice temporário: não toca no índice de produção (data/chroma_db)
    import shutil
    import tempfile

    tmp = Path(tempfile.mkdtemp(prefix="susana-calib-"))
    try:
        retriever = ChromaRetriever(embedder, tmp)
        retriever.index(blocks)
        queries = embedder.encode_queries([expand_acronyms(it["query"]) for it in items])  # igual à produção
        results = [retriever.search(v, k=settings.top_k, query_text=it["query"]) for v, it in zip(queries, items)]
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    # Mesma regra de is_relevant: a menor distância entre os k trechos entregues ao LLM
    dist = np.array([min(x.distance for x in r) if r else 2.0 for r in results])
    accepted_at = lambda t: np.array([is_relevant(r, it["query"], t) for r, it in zip(results, items)])

    is_in = np.array([it["in_domain"] for it in items])
    d_in, d_out = dist[is_in], dist[~is_in]
    logger.info("Corpus: %d blocos | dentro do tema: %d | fora: %d", len(blocks), len(d_in), len(d_out))
    logger.info("Distância dentro do tema: min %.3f  mediana %.3f  max %.3f", d_in.min(), np.median(d_in), d_in.max())
    logger.info("Distância fora do tema:   min %.3f  mediana %.3f  max %.3f", d_out.min(), np.median(d_out), d_out.max())

    # Candidatos: o limiar precisa aceitar MIN_IN_DOMAIN_ACCEPTED do tema; entre esses, o que mais recusa fora do tema
    candidates = np.round(np.arange(0.30, 1.21, 0.01), 2)
    best = None
    for t in candidates:
        acc = accepted_at(t)
        accept_in = float(acc[is_in].mean())
        reject_out = float((~acc[~is_in]).mean())
        if accept_in >= MIN_IN_DOMAIN_ACCEPTED and (best is None or reject_out > best[2]):
            best = (t, accept_in, reject_out)
    t, accept_in, reject_out = best

    logger.info("Limiar sugerido: %.2f → aceita %.0f%% do tema, recusa %.0f%% fora do tema", t, accept_in * 100, reject_out * 100)
    acc_best = accepted_at(t)
    for it, d, a in sorted(zip(items, dist, acc_best), key=lambda x: x[1]):
        wrong = bool(a) != it["in_domain"]
        if wrong:
            logger.info("  erro com limiar %.2f: d=%.3f %-5s %s", t, d, "TEMA" if it["in_domain"] else "FORA", it["query"])
    acc_cur = accepted_at(settings.similarity_threshold)
    logger.info("Limiar atual (config): %.2f → aceita %.0f%% do tema, recusa %.0f%% fora",
                settings.similarity_threshold, acc_cur[is_in].mean() * 100, (~acc_cur[~is_in]).mean() * 100)

    os.makedirs(settings.mlflow_artifact_root, exist_ok=True)
    mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
    mlflow.set_experiment("susana-threshold-calibration")
    with mlflow.start_run():
        mlflow.log_params({"embedding_model": settings.embedding_model, "n_blocks": len(blocks),
                           "n_in": len(d_in), "n_out": len(d_out), "min_in_accepted": MIN_IN_DOMAIN_ACCEPTED})
        mlflow.log_metrics({"suggested_threshold": t, "accept_in_domain": accept_in, "reject_out_domain": reject_out,
                            "d_in_max": float(d_in.max()), "d_out_min": float(d_out.min())})
    print(f"SUGGESTED_SIMILARITY_THRESHOLD={t:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
