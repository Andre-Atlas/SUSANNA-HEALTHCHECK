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
            ("clf", LogisticRegression(class_weight="balanced", solver="liblinear", random_state=42))
        ])

        pipeline.fit(X_train, y_train)

        # Avaliação no conjunto de teste independente (Hold-Out)
        preds = pipeline.predict(X_test)
        probas = pipeline.predict_proba(X_test)[:, 1]
        
        from sklearn.metrics import accuracy_score, precision_score, recall_score, roc_auc_score, confusion_matrix
        from sklearn.model_selection import StratifiedKFold, cross_validate

        acc = accuracy_score(y_test, preds)
        prec = precision_score(y_test, preds)
        rec = recall_score(y_test, preds)
        f1 = f1_score(y_test, preds)
        auc = roc_auc_score(y_test, probas)
        tn, fp, fn, tp = confusion_matrix(y_test, preds).ravel()

        # Validação Cruzada Estratificada (5 Folds) para estabilidade
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        cv_scores = cross_validate(
            pipeline, df["text"], df["target"], cv=cv,
            scoring=["accuracy", "precision", "recall", "f1"]
        )

        print("\n" + classification_report(y_test, preds, target_names=["ADMIN", "CLINICAL"]))
        print(f"Test Metrics: Acc={acc:.3f}, Prec={prec:.3f}, Rec={rec:.3f}, F1={f1:.3f}, AUC={auc:.3f}")
        print(f"5-Fold CV F1: {cv_scores['test_f1'].mean():.3f} (+/- {cv_scores['test_f1'].std():.3f})")
        logger.info("\n%s", classification_report(y_test, preds, target_names=["ADMIN", "CLINICAL"]))
        logger.info("Test Metrics: Acc=%.3f, Prec=%.3f, Rec=%.3f, F1=%.3f, AUC=%.3f", acc, prec, rec, f1, auc)
        logger.info("5-Fold CV F1: %.3f (+/- %.3f)", cv_scores["test_f1"].mean(), cv_scores["test_f1"].std())

        # Exportação direta em .pkl para uso autônomo e entregável
        import joblib
        pkl_path = ROOT / "data" / "guardrail_model.pkl"
        joblib.dump(pipeline, pkl_path)
        
        # Cópia para raiz models/
        root_models_path = ROOT.parent / "models" / "guardrail_model.pkl"
        root_models_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(pipeline, root_models_path)
        logger.info("Modelo serializado exportado com sucesso em: %s e %s", pkl_path, root_models_path)

        # Logs detalhados no MLflow
        mlflow.log_params({
            "model_type": "LogisticRegression",
            "vectorizer": "TfidfVectorizer",
            "ngram_range": "(1, 2)",
            "class_weight": "balanced",
            "cv_folds": 5,
            "train_samples": len(X_train),
            "test_samples": len(X_test),
            "random_state": 42
        })
        
        mlflow.log_metrics({
            "test_accuracy": acc,
            "test_precision": prec,
            "test_recall_clinical": rec,
            "test_f1_score": f1,
            "test_roc_auc": auc,
            "confusion_tp": int(tp),
            "confusion_tn": int(tn),
            "confusion_fp": int(fp),
            "confusion_fn": int(fn),
            "cv_f1_mean": float(cv_scores["test_f1"].mean()),
            "cv_f1_std": float(cv_scores["test_f1"].std()),
            "cv_accuracy_mean": float(cv_scores["test_accuracy"].mean()),
            "cv_recall_mean": float(cv_scores["test_recall"].mean()),
            "cv_precision_mean": float(cv_scores["test_precision"].mean())
        })

        mlflow.set_tags({
            "project": "susana-rag",
            "component": "guardrails",
            "task": "clinical-intent-classification"
        })

        mlflow.sklearn.log_model(pipeline, "model", registered_model_name="susana-guardrail")

        # Promotion Gate Relativo (Fase 4 do MLE Workflow / MLOps)
        client = mlflow.client.MlflowClient()
        model_name = "susana-guardrail"
        champion_f1 = 0.85
        try:
            champ_version_info = client.get_model_version_by_alias(model_name, "champion")
            champ_run = client.get_run(champ_version_info.run_id)
            champion_f1 = float(champ_run.data.metrics.get("cv_f1_mean", 0.85))
            logger.info("Champion atual encontrado (v%s, CV F1: %.3f)", champ_version_info.version, champion_f1)
        except Exception:
            logger.info("Nenhum champion anterior com métricas encontrado. Utilizando baseline de referência: %.3f", champion_f1)

        candidate_f1 = float(cv_scores["test_f1"].mean())
        # Requisitos: F1 >= Champion - 0.02 e Recall Clínico no Teste >= 0.95 (Fail-closed de segurança clínica)
        approved = (candidate_f1 >= (champion_f1 - 0.02)) and (rec >= 0.95) and (candidate_f1 >= 0.85)

        if approved:
            msg = f"Modelo APROVADO no Gate Relativo (CV F1: {candidate_f1:.3f} vs Champ: {champion_f1:.3f}, Rec Clínico: {rec:.3f}). Promovendo para @champion."
            print(msg)
            logger.info(msg)
            versions = client.search_model_versions(f"name='{model_name}'")
            latest_version = max(int(v.version) for v in versions)
            client.set_registered_model_alias(model_name, "champion", str(latest_version))
            print(f"Alias @champion atribuído à versão {latest_version}")
            logger.info("Alias @champion atribuído à versão %s", latest_version)
        else:
            msg = f"Modelo REPROVADO no Gate (CV F1: {candidate_f1:.3f} vs Champ: {champion_f1:.3f}, Rec Clínico: {rec:.3f}). Não promovido."
            print(msg)
            logger.warning(msg)

if __name__ == "__main__":
    main()
