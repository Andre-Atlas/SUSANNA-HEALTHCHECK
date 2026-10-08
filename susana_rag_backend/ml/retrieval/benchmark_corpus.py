#!/usr/bin/env python3
"""Fast retrieval stress check against administrative CSV entities."""
from __future__ import annotations

import json
import re
import statistics
import tempfile
import time
import unicodedata
from pathlib import Path

from app.config import get_settings
from app.rag.corpus import discover_corpus_files, load_corpus
from app.rag.embeddings import Embedder
from app.rag.retriever import ChromaRetriever, is_relevant

ROOT = Path(__file__).resolve().parents[3]
CORPUS_DIR = ROOT / "CORPUS" / "Arquivos"
ENTITY_FIELDS = ("Estabelecimento", "Centros Especializado", "Unidades de Pronto Atendimento")
OUT_OF_DOMAIN_QUERIES = (
    "Qual o horário do metrô de Brasília?",
    "Qual a previsão do tempo para amanhã?",
    "Como faço um bolo de chocolate?",
    "Qual foi o resultado do jogo de futebol?",
    "Onde renovo minha carteira de motorista?",
    "Qual o preço da passagem aérea para São Paulo?",
    "Como declaro imposto de renda?",
    "Quais filmes estão no cinema hoje?",
    "Como configuro uma rede Wi-Fi?",
    "Qual a cotação do dólar agora?",
    "Onde encontro uma oficina mecânica?",
    "Qual o cardápio do restaurante mais próximo?",
)


def _normalize(text: str) -> str:
    text = "".join(
        char
        for char in unicodedata.normalize("NFKD", text).casefold()
        if not unicodedata.combining(char)
    )
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


def _entity_name(block_text: str) -> str | None:
    fields = "|".join(re.escape(field) for field in ENTITY_FIELDS)
    match = re.search(rf"(?:{fields}):\s*([^;\n]+)", block_text, re.IGNORECASE)
    return match.group(1).strip() if match else None


def main() -> None:
    settings = get_settings()
    files = discover_corpus_files([CORPUS_DIR])
    blocks = load_corpus(files)
    cases = [
        {"category": "entity", "name": name, "query": f"Onde fica {name}?", "block_id": block.id}
        for block in blocks
        if block.tag == "CSV"
        if (name := _entity_name(block.text))
    ]
    faq_path = CORPUS_DIR / "meu_sus_digital_faq_estruturado.json"
    if faq_path.exists():
        faq_blocks = {}
        for block in blocks:
            match = re.search(r"\(item (\d+)\.", block.header)
            if block.tag == "FAQ" and match:
                faq_blocks.setdefault(int(match.group(1)), block)
        faq_items = json.loads(faq_path.read_text(encoding="utf-8")).get("documentos", [])
        cases.extend(
            {
                "category": "faq",
                "name": item.get("id", f"faq-{index}"),
                "query": item["pergunta"],
                "block_id": faq_blocks[index].id,
            }
            for index, item in enumerate(faq_items, 1)
            if index in faq_blocks and item.get("pergunta")
        )
    if not cases:
        raise SystemExit(f"Nenhuma entidade extraída de {CORPUS_DIR}")

    embedder = Embedder(settings.embedding_model, settings.embedding_max_seq_length)
    query_vectors = embedder.encode_queries([case["query"] for case in cases] + list(OUT_OF_DOMAIN_QUERIES))
    with tempfile.TemporaryDirectory(prefix="susana-retrieval-eval-") as temp_dir:
        retriever = ChromaRetriever(embedder, Path(temp_dir), collection_prefix="gold")
        started = time.perf_counter()
        retriever.index(blocks, batch_size=128)
        index_ms = round((time.perf_counter() - started) * 1000)

        latencies = []
        hits_by_category = {"entity": {"top1": 0, "top3": 0}, "faq": {"top1": 0, "top3": 0}}
        misses = []
        for index, case in enumerate(cases):
            started = time.perf_counter()
            results = retriever.search(query_vectors[index], k=3, query_text=case["query"])
            latencies.append((time.perf_counter() - started) * 1000)
            found_at = next(
                (rank for rank, result in enumerate(results, 1) if result.id == case["block_id"]),
                None,
            )
            category_hits = hits_by_category[case["category"]]
            category_hits["top1"] += found_at == 1
            category_hits["top3"] += found_at is not None
            if found_at is None:
                misses.append({
                    "query": case["query"],
                    "source_id": case["block_id"],
                    "top_candidates": [
                        {
                            "source": result.source,
                            "distance": round(result.distance, 3),
                            "text": result.text[:180],
                        }
                        for result in results
                    ],
                })

        out_domain_start = len(cases)
        out_domain_accepted = 0
        for offset, query in enumerate(OUT_OF_DOMAIN_QUERIES):
            results = retriever.search(
                query_vectors[out_domain_start + offset], k=3, query_text=query
            )
            out_domain_accepted += is_relevant(results, query, settings.similarity_threshold)

    latencies.sort()
    p95_index = min(len(latencies) - 1, int(len(latencies) * 0.95))
    entity_cases = sum(case["category"] == "entity" for case in cases)
    faq_cases = sum(case["category"] == "faq" for case in cases)
    print(json.dumps({
        "source_files": len(files),
        "indexed_blocks": len(blocks),
        "entity_cases": entity_cases,
        "entity_recall_at_1": round(hits_by_category["entity"]["top1"] / entity_cases, 4),
        "entity_recall_at_3": round(hits_by_category["entity"]["top3"] / entity_cases, 4),
        "faq_cases": faq_cases,
        "faq_recall_at_1": round(hits_by_category["faq"]["top1"] / faq_cases, 4) if faq_cases else 0,
        "faq_recall_at_3": round(hits_by_category["faq"]["top3"] / faq_cases, 4) if faq_cases else 0,
        "total_eval_cases": len(cases),
        "out_of_domain_cases": len(OUT_OF_DOMAIN_QUERIES),
        "out_of_domain_accepted": out_domain_accepted,
        "search_p50_ms": round(statistics.median(latencies), 2),
        "search_p95_ms": round(latencies[p95_index], 2),
        "temporary_index_ms": index_ms,
        "production_index_touched": False,
        "misses": misses[:20],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()