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
    # 30 s: com o corpus integrado os trechos são maiores e o 1º token passou de 12 s em 3 de 87 perguntas
    llm_timeout_s: float = 30.0
    llm_keep_alive: str = "30m"
    llm_num_predict: int = 350

    # Retrieval
    embedding_model: str = "paraphrase-multilingual-MiniLM-L12-v2"
    # Tokens lidos por bloco (padrão do modelo: 128, que cortava 41 de 52 blocos). Vindo da develop_gui_sam.
    embedding_max_seq_length: int = 256
    similarity_threshold: float = 0.74  # calibrado por ml/retrieval/calibrate_threshold.py (corpus de 1.948 blocos)
    top_k: int = 3
    docs_dir: Path = BACKEND_DIR / "data" / "corpus"
    # Corpus curado (CSV/JSON de unidades, FAQ, REME), vindo da develop_gui_sam. As bases de análise
    # (SIA, óbitos, exames) ficam FORA de propósito — veja docs/12-comparacao-develop_gui_sam.md.
    project_corpus_dir: Path = BACKEND_DIR.parent / "CORPUS" / "Arquivos"
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


    @property
    def corpus_roots(self) -> list[Path]:
        """Pastas varridas (recursivamente) na indexação."""
        return [self.docs_dir, self.project_corpus_dir]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
