"""Configuração tipada da Susana (lida de variáveis de ambiente / .env)."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BACKEND_DIR / ".env"), env_file_encoding="utf-8", extra="ignore"
    )

    environment: str = "development"

    # LLM local (Ollama)
    llm_provider: str = "ollama"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"
    llm_timeout_s: float = 12.0
    llm_keep_alive: str = "30m"
    llm_num_predict: int = 350

    # Retrieval
    embedding_model: str = "paraphrase-multilingual-MiniLM-L12-v2"
    similarity_threshold: float = 0.70  # calibrado por ml/retrieval/calibrate_threshold.py
    top_k: int = 3
    docs_dir: Path = BACKEND_DIR / "data" / "corpus"
    chroma_dir: Path = BACKEND_DIR / "data" / "chroma_db"

    # Guardrail
    guardrail_model_uri: str = "models:/susana-guardrail@champion"
    guardrail_enabled_ml: bool = True
    guardrail_threshold: float = 0.4        # p(clínica) a partir da qual o ML bloqueia (calibrado no treino)
    # Gates de promoção (openspec/changes/susana-local-llm-ml/contracts.md §4)
    guardrail_gate_recall_clinical: float = 0.98
    guardrail_gate_precision_admin: float = 0.95
    # Não está no contrato original: as duas métricas acima só penalizam clínicas liberadas;
    # esta impede um modelo que "bloqueia tudo" de passar no gate.
    guardrail_gate_admin_allowed: float = 0.80

    # MLOps
    mlflow_tracking_uri: str = "sqlite:///" + str(BACKEND_DIR / "mlflow.db")
    mlflow_artifact_root: Path = BACKEND_DIR / "mlruns"
    mlflow_log_requests: bool = True
    # LGPD: por padrão registra só hash + tamanho da pergunta, nunca o texto
    mlflow_log_query_text: bool = False


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
