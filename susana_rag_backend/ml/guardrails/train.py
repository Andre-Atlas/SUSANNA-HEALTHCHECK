#!/usr/bin/env python3
"""
Treinamento do Classificador de Guardrails (Scikit-Learn).

1. Carrega data/guardrails_dataset.csv (label: 1 = clínica, 0 = administrativa).
2. Avalia com validação cruzada estratificada (5 folds) a DECISÃO HÍBRIDA usada em
   produção (`app.rag.guardrails.decide`: regras + ML), não só o modelo isolado.
3. Treina o modelo final com todos os dados e registra no MLflow.
4. Gate de promoção (contracts.md §4): só aplica o alias @champion se
   recall clínico e precisão administrativa do híbrido atingirem os mínimos.

Uso: python -m ml.guardrails.train
"""
import logging
import os
from pathlib import Path

import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_score, recall_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import Pipeline

from app.config import get_settings
from app.rag.guardrails import decide

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger("susana.ml.train")

ROOT = Path(__file__).resolve().parent.parent.parent
DATA_PATH = ROOT / "data" / "guardrails_dataset.csv"
MODEL_NAME = "susana-guardrail"
LABELS = {"1": 1, "0": 0, "CLINICAL": 1, "ADMINISTRATIVE": 0}


def build_pipeline() -> Pipeline:
    return Pipeline([
        # char n-grams toleram erros de digitação e variações ("remedio", "remédios")
        ("tfidf", TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), sublinear_tf=True, lowercase=True)),
        ("clf", LogisticRegression(class_weight="balanced", C=4.0, max_iter=1000, random_state=42)),
    ])


def load_dataset() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH, dtype=str)
    unknown = sorted(set(df["label"].str.strip()) - set(LABELS))
    if unknown:
        raise ValueError(f"Rótulos desconhecidos no dataset: {unknown}")
    df["target"] = df["label"].str.strip().map(LABELS).astype(int)
    df["text"] = df["text"].str.strip()
    dupes = df["text"].str.lower().duplicated().sum()
    if dupes:
        raise ValueError(f"{dupes} frases duplicadas no dataset")
    return df


CV_SEEDS = (0, 1, 2)  # média de 3 repetições: com ~100 frases, um único split oscila muito


def metrics(y_true, y_pred, prefix: str) -> dict:
    return {
        f"{prefix}_recall_clinical": recall_score(y_true, y_pred, pos_label=1),
        f"{prefix}_precision_admin": precision_score(y_true, y_pred, pos_label=0, zero_division=0),
        f"{prefix}_admin_allowed": recall_score(y_true, y_pred, pos_label=0),
    }


def main() -> int:
    settings = get_settings()
    os.makedirs(settings.mlflow_artifact_root, exist_ok=True)
    mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
    mlflow.set_experiment("susana-guardrails-train")

    df = load_dataset()
    X, y = df["text"].tolist(), df["target"].to_numpy()
    logger.info("Dataset: %d frases (%d clínicas, %d administrativas)", len(y), y.sum(), len(y) - y.sum())

    thr = settings.guardrail_threshold
    runs = []
    for seed in CV_SEEDS:
        # Probabilidades out-of-fold: cada frase é prevista por um modelo que não a viu no treino
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=seed)
        p = cross_val_predict(build_pipeline(), X, y, cv=cv, method="predict_proba")[:, 1]
        decs = [decide(t, q, thr) for t, q in zip(X, p)]
        hyb = np.array([int(d.blocked) for d in decs])
        runs.append((p, decs, {**metrics(y, (p >= thr).astype(int), "cv_ml_only"), **metrics(y, hyb, "cv_hybrid")}))

    m = {k: float(np.mean([r[2][k] for r in runs])) for k in runs[0][2]}
    for k, v in m.items():
        logger.info("%-32s %.3f", k, v)

    # Erros detalhados da 1ª repetição (para orientar a curadoria do dataset)
    p_oof, decisions, _ = runs[0]
    pred_hybrid = np.array([int(d.blocked) for d in decisions])

    errors = df.assign(p=p_oof.round(2), blocked=pred_hybrid, reason=[d.reason for d in decisions])
    errors = errors[errors["blocked"] != errors["target"]]
    for _, r in errors.iterrows():
        kind = "FALSO NEGATIVO (clínica liberada)" if r.target == 1 else "falso positivo (admin bloqueada)"
        logger.info("  %s p=%.2f %s: %s", kind, r.p, r.reason, r.text)

    gate_ok = (
        m["cv_hybrid_recall_clinical"] >= settings.guardrail_gate_recall_clinical
        and m["cv_hybrid_precision_admin"] >= settings.guardrail_gate_precision_admin
        and m["cv_hybrid_admin_allowed"] >= settings.guardrail_gate_admin_allowed
    )

    with mlflow.start_run() as run:
        logger.info("Run ID: %s", run.info.run_id)
        final = build_pipeline().fit(X, y)
        mlflow.log_params({
            "model_type": "LogisticRegression",
            "vectorizer": "TfidfVectorizer(char_wb, 2-5)",
            "threshold": thr,
            "n_samples": len(y),
            "cv_folds": 5,
            "gate_recall_clinical": settings.guardrail_gate_recall_clinical,
            "gate_precision_admin": settings.guardrail_gate_precision_admin,
            "gate_admin_allowed": settings.guardrail_gate_admin_allowed,
            "cv_repeats": len(CV_SEEDS),
            "gate_passed": gate_ok,
        })
        mlflow.log_metrics(m)
        info = mlflow.sklearn.log_model(final, name="model", registered_model_name=MODEL_NAME)
        version = str(info.registered_model_version)

        client = mlflow.MlflowClient()
        if gate_ok:
            client.set_registered_model_alias(MODEL_NAME, "champion", version)
            logger.info("Gate APROVADO → versão %s promovida para @champion.", version)
        else:
            logger.warning(
                "Gate REPROVADO (recall clínico %.3f/%.2f, precisão admin %.3f/%.2f, admin liberadas %.3f/%.2f). "
                "Versão %s registrada, mas @champion NÃO foi alterado.",
                m["cv_hybrid_recall_clinical"], settings.guardrail_gate_recall_clinical,
                m["cv_hybrid_precision_admin"], settings.guardrail_gate_precision_admin,
                m["cv_hybrid_admin_allowed"], settings.guardrail_gate_admin_allowed, version,
            )
    return 0 if gate_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
