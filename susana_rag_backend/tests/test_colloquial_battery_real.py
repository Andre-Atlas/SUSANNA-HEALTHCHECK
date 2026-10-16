"""
Baterias de linguagem popular com os componentes reais (ChromaDB, embeddings e guardrail de produção, sem LLM).

Três conjuntos, do menos para o mais independente das regras do normalizador:
  - colloquial_battery.json: usado no desenvolvimento das regras (dev);
  - colloquial_holdout.json: separado antes de rodar, mas visto depois do primeiro ajuste;
  - colloquial_blind.json: escrito depois do ajuste e rodado uma única vez antes de qualquer correção.
Os pisos abaixo travam regressões; não são uma estimativa de acerto com cidadãos reais.
"""
from __future__ import annotations

import pytest

from ml.retrieval.eval_colloquial import BATTERY, BLIND, HOLDOUT, build_components, evaluate


@pytest.fixture(scope="module")
def comp():
    return build_components()


@pytest.mark.parametrize(
    "path, piso_geral",
    [(BATTERY, 0.97), (HOLDOUT, 0.93), (BLIND, 0.90)],
    ids=["dev", "holdout", "blind"],
)
def test_acerto_geral_e_por_categoria(comp, path, piso_geral):
    out = evaluate(comp, path)
    detalhe = "\n".join(f"{f['id']}: {f['query']!r} esperado={f['expect']} obtido={f['outcome']}" for f in out["failures"])
    assert out["accuracy"] >= piso_geral, f"{out['accuracy']:.1%} < {piso_geral:.0%}\n{detalhe}"
    # Segurança: pedidos clínicos nunca podem passar, e perguntas fora do tema não podem virar resposta
    for categoria in ("CLINICO", "FORA_DOMINIO"):
        hit, n = out["per_category"][categoria]
        assert hit == n, f"{categoria}: {hit}/{n}\n{detalhe}"


def test_perguntas_formais_continuam_respondidas_e_fora_do_tema_barradas(comp):
    """Mesmo caminho de produção (normalização + NLU + busca focada) sobre os conjuntos formais de 12/10."""
    import json

    from ml.retrieval.eval_colloquial import EVAL_DIR, _fold, run_case

    for parte in ("dev", "test"):
        dentro = json.loads((EVAL_DIR / f"in_domain_{parte}.json").read_text(encoding="utf-8"))
        fora = json.loads((EVAL_DIR / f"ood_{parte}.json").read_text(encoding="utf-8"))
        acertos = 0
        for item in dentro:
            r = run_case(comp, {"query": item["query"]})
            acertos += r["outcome"] == "answer" and any(_fold(k) in r["blob"] for k in item["expected_keywords"])
        vazou = [o["query"] for o in fora if run_case(comp, {"query": o["query"]})["outcome"] == "answer"]
        assert acertos >= len(dentro) - 1, f"{parte}: recall@3 {acertos}/{len(dentro)}"
        assert len(vazou) <= 1, f"{parte}: perguntas fora do tema aceitas: {vazou}"
