"""Contratos formais de dados para ingestão autônoma e webhooks."""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, HttpUrl, field_validator


class SUSDataTag(str, Enum):
    UNIDADE = "UNIDADE"
    VACINACAO = "VACINACAO"
    SERVICO = "SERVICO"
    MEDICAMENTO = "MEDICAMENTO"
    EPIDEMIOLOGIA = "EPIDEMIOLOGIA"
    INSTITUCIONAL = "INSTITUCIONAL"
    EMERGENCIA = "EMERGENCIA"


ALLOWED_SUS_DOMAINS = (
    "saude.df.gov.br",
    "dados.df.gov.br",
    "gov.br",
    "ebserh.gov.br",
    "fiocruz.br",
    "anvisa.gov.br",
    "agenciabrasilia.df.gov.br",
    "testserver",
)


class RawDocumentPayload(BaseModel):
    """Payload de entrada de um documento para ingestão no ecossistema SUS."""
    title: str = Field(..., min_length=3, max_length=300, description="Título oficial do documento ou comunicado")
    text: str = Field(..., min_length=50, description="Conteúdo textual limpo e relevante")
    source_url: str = Field(..., description="URL oficial de proveniência (SES-DF, MS, CKAN)")
    tag: SUSDataTag = Field(default=SUSDataTag.INSTITUCIONAL, description="Classificação semântica do documento")
    author_or_department: Optional[str] = Field(default=None, description="Órgão ou diretoria emissora")
    fetched_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Data/hora da coleta")

    @field_validator("source_url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        from urllib.parse import urlparse
        v_str = str(v).strip()
        if not (v_str.startswith("http://") or v_str.startswith("https://")):
            raise ValueError("source_url deve iniciar com http:// ou https://")
        parsed = urlparse(v_str)
        hostname = (parsed.hostname or "").lower()
        if not any(hostname == allowed or hostname.endswith("." + allowed) for allowed in ALLOWED_SUS_DOMAINS):
            raise ValueError(
                f"Domínio '{hostname}' não autorizado para ingestão. "
                f"Permitidos apenas domínios oficiais do ecossistema SUS: {ALLOWED_SUS_DOMAINS}"
            )
        return v_str


class IngestionResult(BaseModel):
    """Resposta estruturada sobre o resultado do processamento do documento."""
    status: str = Field(..., description="'success', 'skipped' ou 'error'")
    document_id: str = Field(..., description="Hash SHA-256 identificador único do documento")
    chunks_created: int = Field(default=0, description="Quantidade de blocos semânticos indexados no ChromaDB")
    is_duplicate: bool = Field(default=False, description="True se o documento já constava no manifesto com mesmo hash")
    message: str = Field(..., description="Descrição legível da operação")
