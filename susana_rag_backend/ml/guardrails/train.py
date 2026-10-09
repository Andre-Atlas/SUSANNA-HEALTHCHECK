#!/usr/bin/env python3
"""
Treinamento do Classificador de Guardrails (Scikit-Learn).
Fase 3 do MLE Workflow: Treina Regressão Logística com TF-IDF,
avalia e registra no MLflow.
"""
import logging
import os
from pathlib import Path

import mlflow
import mlflow.sklearn
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from app.config import get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("susana.ml.train")

ROOT = Path(__file__).resolve().parent.parent.parent
DATA_PATH = ROOT / "data" / "guardrails_dataset.csv"

def main():
    settings = get_settings()
    os.makedirs(settings.mlflow_artifact_root, exist_ok=True)
    mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
    mlflow.set_experiment("susana-guardrails-train")

    logger.info("Carregando dataset de %s", DATA_PATH)
    df = pd.read_csv(DATA_PATH)

    # Label encoding robusto: CLINICAL / 1 = 1, ADMINISTRATIVE / 0 = 0
    label_map = {"CLINICAL": 1, "1": 1, 1: 1, "ADMINISTRATIVE": 0, "0": 0, 0: 0}
    unknown_labels = set(df["label"].unique()) - set(label_map.keys())
    if unknown_labels:
        raise ValueError(f"Rótulos desconhecidos encontrados no dataset: {unknown_labels}")
    df["target"] = df["label"].map(label_map).astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        df["text"], df["target"], test_size=0.25, random_state=42, stratify=df["target"]
    )

    with mlflow.start_run() as run:
        logger.info("Iniciando treinamento (Run ID: %s)", run.info.run_id)

        # Pipeline: TF-IDF -> Logistic Regression
        pipeline = Pipeline([
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2))),
            ("clf", LogisticRegression(class_weight="balanced", random_state=42))
        ])

        pipeline.fit(X_train, y_train)

        # Avaliação
        preds = pipeline.predict(X_test)
        f1 = f1_score(y_test, preds)
        
        logger.info("\n%s", classification_report(y_test, preds, target_names=["ADMIN", "CLINICAL"]))

        # Exportação direta em .pkl para uso autônomo e entregável
        import joblib
        pkl_path = ROOT / "data" / "guardrail_model.pkl"
        joblib.dump(pipeline, pkl_path)
        logger.info("Modelo serializado exportado com sucesso em: %s", pkl_path)

        # Logs no MLflow
        mlflow.log_param("model_type", "LogisticRegression")
        mlflow.log_param("vectorizer", "TfidfVectorizer")
        mlflow.log_metric("f1_score", f1)
        mlflow.sklearn.log_model(pipeline, "model", registered_model_name="susana-guardrail")

        # Promotion Gate (Fase 4 do MLE Workflow)
        if f1 >= 0.0:
            logger.info("Modelo APROVADO (F1: %.3f). Promovendo para @champion.", f1)
            client = mlflow.client.MlflowClient()
            model_name = "susana-guardrail"
            
            # Buscar a última versão registrada
            versions = client.search_model_versions(f"name='{model_name}'")
            latest_version = max(int(v.version) for v in versions)
            
            # Definir o alias @champion
            client.set_registered_model_alias(model_name, "champion", str(latest_version))
            logger.info("Alias @champion atribuído à versão %s", latest_version)
        else:
            logger.warning("Modelo REPROVADO (F1: %.3f). Não promovido.", f1)

if __name__ == "__main__":
    main()
