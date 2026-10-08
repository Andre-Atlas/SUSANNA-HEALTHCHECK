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
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"
    llm_timeout_s: float = 12.0
    llm_keep_alive: str = "30m"
    llm_num_predict: int = 350

    # Retrieval
    embedding_model: str = "paraphrase-multilingual-MiniLM-L12-v2"
    embedding_max_seq_length: int = 512
    similarity_threshold: float = 0.55
    top_k: int = 3
    docs_dir: Path = BACKEND_DIR / "data" / "corpus"
    project_corpus_dir: Path = BACKEND_DIR.parent / "CORPUS"
    legacy_docs_file: Path = BACKEND_DIR / "data" / "sus_docs.txt"
    chroma_dir: Path = BACKEND_DIR / "data" / "chroma_db"

    # Guardrail
    guardrail_model_uri: str = "models:/susana-guardrail@champion"
    guardrail_enabled_ml: bool = True

    # MLOps
    mlflow_tracking_uri: str = "sqlite:///" + str(BACKEND_DIR / "mlflow.db")
    mlflow_artifact_root: Path = BACKEND_DIR / "mlruns"
    mlflow_log_requests: bool = True


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
