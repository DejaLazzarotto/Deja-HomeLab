"""Cria a tabela de empresas.

Revision ID: 20260809_0001
Revises:
Create Date: 2026-08-09
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260809_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Cria a estrutura persistente inicial de empresas."""

    op.create_table(
        "companies",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("legal_name", sa.String(length=255), nullable=False),
        sa.Column("trade_name", sa.String(length=255), nullable=False),
        sa.Column("document", sa.String(length=14), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=20), nullable=True),
        sa.Column(
            "status",
            sa.Enum("active", "inactive", name="company_status"),
            nullable=False,
            server_default="active",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text(
                "CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"
            ),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "document",
            name="uq_companies_document",
        ),
    )

    op.create_index(
        "ix_companies_document",
        "companies",
        ["document"],
        unique=False,
    )


def downgrade() -> None:
    """Remove a estrutura persistente de empresas."""

    op.drop_index("ix_companies_document", table_name="companies")
    op.drop_table("companies")