from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Susana API"
    app_version: str = "0.2.0"
    debug: bool = False

    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/susana"
    )

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = ""
    ollama_timeout_seconds: float = 60.0

    embedding_provider: str = "ollama"
    embedding_model: str = ""
    embedding_dimensions: int = 768

    ckan_base_url: str = ""

    rag_top_k: int = 5
    rag_similarity_threshold: float = 0.70
    rag_chunk_size: int = 1200
    rag_chunk_overlap: int = 150

    cors_origins: str = "http://localhost:3000,http://localhost:5173"
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
