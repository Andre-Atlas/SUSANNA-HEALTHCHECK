"""Configuração tipada da Susana (lida de variáveis de ambiente / .env)."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parent.parent


# Valor de desenvolvimento (público no repositório): em produção é recusado.
DEFAULT_INGESTION_KEY = "susana-ingest-secret-2026"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BACKEND_DIR / ".env"), env_file_encoding="utf-8", extra="ignore"
    )

    environment: str = "development"
    cors_origins: str = "*"

    # LLM local (Ollama)
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"
    llm_timeout_s: float = 12.0
    llm_keep_alive: str = "30m"
    llm_num_predict: int = 350

    # Retrieval
    embedding_model: str = "paraphrase-multilingual-MiniLM-L12-v2"
    embedding_max_seq_length: int = 512
    similarity_threshold: float = 0.65
    top_k: int = 3
    docs_dir: Path = BACKEND_DIR / "data" / "corpus"
    project_corpus_dir: Path = (
        (BACKEND_DIR.parent / "CORPUS" / "Arquivos")
        if (BACKEND_DIR.parent / "CORPUS" / "Arquivos").exists()
        else (BACKEND_DIR.parent / "CORPUS")
    )
    legacy_docs_file: Path = BACKEND_DIR / "data" / "sus_docs.txt"
    chroma_dir: Path = Field(
        default=BACKEND_DIR / "data" / "chroma_db",
        validation_alias=AliasChoices("chroma_dir", "CHROMA_DIR", "CHROMA_PERSIST_DIRECTORY"),
    )
    # SQLite de contas, agenda e vigilância (em produção fica num volume próprio)
    app_db_path: Path = Field(
        default=BACKEND_DIR / "data" / "susana_app.db",
        validation_alias=AliasChoices("app_db_path", "APP_DB_PATH"),
    )

    # Guardrail
    guardrail_model_uri: str = "models:/susana-guardrail@champion"
    guardrail_enabled_ml: bool = True

    # Ingestão Autônoma & Segurança
    ingestion_api_key: Optional[str] = Field(
        default=DEFAULT_INGESTION_KEY,
        validation_alias=AliasChoices("ingestion_api_key", "INGESTION_API_KEY", "INGESTION_SECRET_KEY"),
    )
    relevance_confident_threshold: float = 0.35

    # Cadastro opcional / sessões de login
    auth_session_days_remember: int = 30
    auth_session_hours_default: int = 24

    # Pesquisa Online Assíncrona & Complementação de Base
    online_search_enabled: bool = True
    online_search_timeout_s: float = 3.5
    online_search_max_results: int = 3
    online_search_auto_ingest: bool = True

    # MLOps
    mlflow_tracking_uri: str = "sqlite:///" + str(BACKEND_DIR / "mlflow.db")
    mlflow_artifact_root: Path = BACKEND_DIR / "mlruns"
    mlflow_log_requests: bool = True


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
