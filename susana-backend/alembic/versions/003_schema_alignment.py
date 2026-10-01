"""Align ORM metadata with the existing database schema.

Revision ID: 003_schema_alignment
Revises: 002_backend_hardening
Create Date: 2026-10-01
"""
from alembic import op
import sqlalchemy as sa

revision = "003_schema_alignment"
down_revision = "002_backend_hardening"
branch_labels = None
depends_on = None


TIMESTAMP_COLUMNS = {
    "document_chunks": ("created_at",),
    "documents": ("collected_at", "created_at", "updated_at"),
    "establishments": ("created_at", "updated_at"),
    "services": ("created_at", "updated_at"),
    "sources": ("created_at", "updated_at"),
}


def upgrade() -> None:
    for table, columns in TIMESTAMP_COLUMNS.items():
        for column in columns:
            op.execute(
                sa.text(
                    f'UPDATE "{table}" SET "{column}" = CURRENT_TIMESTAMP '
                    f'WHERE "{column}" IS NULL'
                )
            )
            op.alter_column(
                table,
                column,
                existing_type=sa.DateTime(timezone=True),
                existing_nullable=True,
                nullable=False,
            )

    op.create_index("ix_documents_content_hash", "documents", ["content_hash"])
    op.create_index("ix_establishments_external_id", "establishments", ["external_id"])


def downgrade() -> None:
    op.drop_index("ix_establishments_external_id", table_name="establishments")
    op.drop_index("ix_documents_content_hash", table_name="documents")

    for table, columns in reversed(tuple(TIMESTAMP_COLUMNS.items())):
        for column in columns:
            op.alter_column(
                table,
                column,
                existing_type=sa.DateTime(timezone=True),
                existing_nullable=False,
                nullable=True,
            )