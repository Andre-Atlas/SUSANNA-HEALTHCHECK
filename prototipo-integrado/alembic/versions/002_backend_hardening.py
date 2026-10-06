"""backend hardening: source provenance for establishments and cleanup of unused categories

Revision ID: 002_backend_hardening
Revises: 001_initial
Create Date: 2026-09-29
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "002_backend_hardening"
down_revision = "001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "establishments",
        sa.Column("source_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_index("ix_establishments_source_id", "establishments", ["source_id"])
    op.create_foreign_key(
        "fk_establishments_source_id_sources",
        "establishments",
        "sources",
        ["source_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        "uq_document_chunks_document_chunk_index",
        "document_chunks",
        ["document_id", "chunk_index"],
        unique=True,
    )
    op.drop_table("categories")


def downgrade() -> None:
    op.create_table(
        "categories",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(120), nullable=False, unique=True),
    )
    op.drop_index("uq_document_chunks_document_chunk_index", table_name="document_chunks")
    op.drop_constraint("fk_establishments_source_id_sources", "establishments", type_="foreignkey")
    op.drop_index("ix_establishments_source_id", table_name="establishments")
    op.drop_column("establishments", "source_id")
