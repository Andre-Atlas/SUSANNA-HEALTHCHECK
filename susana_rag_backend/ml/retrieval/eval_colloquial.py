#!/usr/bin/env python3
"""
Bateria de linguagem popular: abreviações, urgência, gírias, erros de digitação,
perguntas encadeadas, pedidos clínicos e perguntas fora do domínio.

Reproduz o caminho de /chat/stream sem o LLM:
contextualização -> guardrail -> NLU -> busca vetorial -> filtro de relevância.

    python -m ml.retrieval.eval_colloquial            # imprime o relatório e as falhas
    python -m ml.retrieval.eval_colloquial --mlflow   # registra as métricas no MLflow
"""
from __future__ import annotations

import argparse
import json
import unicodedata
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List

from app.config import get_settings
from app.rag.conversation import ConversationalContextManager
from app.rag.embeddings import Embedder
from app.rag.guardrails import GuardrailsClassifier
from app.rag.nlu import NaturalLanguageInferencer
from app.rag.retriever import ChromaRetriever, is_relevant

EVAL_DIR = Path(__file__).resolve().parents[2] / "data" / "eval"
BATTERY = EVAL_DIR / "colloquial_battery.json"
HOLDOUT = EVAL_DIR / "colloquial_holdout.json"
BLIND = EVAL_DIR / "colloquial_blind.json"


def _fold(text: str) -> str:
    n = unicodedata.normalize("NFKD", text).casefold()
    return "".join(c for c in n if not unicodedata.combining(c))


class _Turn:
    def __init__(self, text: str, user: bool):
        self._t, self._u = text, user

    def get_text(self) -> str:
        return self._t

    def is_user(self) -> bool:
        return self._u


def build_components() -> Dict[str, Any]:
    s = get_settings()
    embedder = Embedder(s.embedding_model, s.embedding_max_seq_length)
    retriever = ChromaRetriever(embedder, s.chroma_dir)
    assert retriever.count() > 0, "ChromaDB vazio: indexe o corpus antes."
    return {"settings": s, "embedder": embedder, "retriever": retriever, "guardrails": GuardrailsClassifier()}


def run_case(comp: Dict[str, Any], case: Dict[str, Any], k: int = 3) -> Dict[str, Any]:
    history = []
    for h in case.get("history", []):
        history.append(_Turn(h, True))
    ctx = ConversationalContextManager.contextualize(case["query"], history)
    if comp["guardrails"].is_clinical(ctx):
        return {"outcome": "blocked", "ctx": ctx, "top": ""}

    from app.rag.normalizer import looks_off_topic

    if looks_off_topic(ctx):
        return {"outcome": "no_result", "ctx": ctx, "top": "", "dist": None}
    nlu = NaturalLanguageInferencer.infer(ctx, history=history)
    q = nlu.expanded_query
    s = comp["settings"]
    vec = comp["embedder"].encode_queries([q])[0]
    ret = comp["retriever"]

    def ok(res):
        return is_relevant(res, q, 0.65, 0.35) or is_relevant(res, ctx, 0.65, 0.35)

    from app.rag.retrieval_flow import search_best

    res = search_best(ret, comp["embedder"], nlu, k, nlu.metadata_filter)
    if not ok(res) and nlu.metadata_filter:
        alt = search_best(ret, comp["embedder"], nlu, k, None)
        if ok(alt):
            res = alt
    if not ok(res):
        return {"outcome": "no_result", "ctx": ctx, "top": "", "dist": res[0].distance if res else None}
    blob = _fold(" ".join(r.text + " " + r.source for r in res[:k]))
    return {"outcome": "answer", "ctx": ctx, "top": res[0].source[:70], "dist": res[0].distance, "blob": blob}


def evaluate(comp: Dict[str, Any], path: Path = BATTERY) -> Dict[str, Any]:
    cases: List[Dict[str, Any]] = json.loads(path.read_text(encoding="utf-8"))
    per_cat: Dict[str, List[bool]] = defaultdict(list)
    failures = []
    for c in cases:
        r = run_case(comp, c)
        if c["expect"] == "answer":
            ok = r["outcome"] == "answer" and any(_fold(kw) in r["blob"] for kw in c["kw"])
        else:
            ok = r["outcome"] == c["expect"] or (c["expect"] == "no_result" and r["outcome"] == "blocked")
        per_cat[c["cat"]].append(ok)
        if not ok:
            failures.append({**c, **{k: v for k, v in r.items() if k != "blob"}})
    total = [x for v in per_cat.values() for x in v]
    return {
        "accuracy": sum(total) / len(total),
        "n": len(total),
        "per_category": {k: (sum(v), len(v)) for k, v in per_cat.items()},
        "failures": failures,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mlflow", action="store_true")
    ap.add_argument("--blind", action="store_true", help="conjunto cego, escrito depois do ajuste (colloquial_blind.json)")
    ap.add_argument("--holdout", action="store_true", help="usa o conjunto cego (colloquial_holdout.json)")
    args = ap.parse_args()
    out = evaluate(build_components(), BLIND if args.blind else HOLDOUT if args.holdout else BATTERY)
    print(f"\nACERTO GERAL: {out['accuracy']:.1%} ({round(out['accuracy'] * out['n'])}/{out['n']})")
    for cat, (hit, n) in out["per_category"].items():
        print(f"  {cat:14s} {hit}/{n}")
    for f in out["failures"]:
        print(f"\nFALHOU [{f['id']}] {f['query']!r} esperado={f['expect']} obtido={f['outcome']} dist={f.get('dist')}\n   ctx={f['ctx'][:140]!r}\n   top={f['top']}")
    if args.mlflow:
        import mlflow
        s = get_settings()
        mlflow.set_tracking_uri(s.mlflow_tracking_uri)
        mlflow.set_experiment("susana-colloquial-battery")
        with mlflow.start_run():
            mlflow.log_metric("accuracy", out["accuracy"])
            for cat, (hit, n) in out["per_category"].items():
                mlflow.log_metric(f"acc_{cat.lower()}", hit / n)


if __name__ == "__main__":
    main()
