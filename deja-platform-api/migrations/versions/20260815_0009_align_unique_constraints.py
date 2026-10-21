"""Alinha restrições únicas de empresas e organizações.

Revision ID: 20260815_0009
Revises: 20260813_0008
Create Date: 2026-08-15
"""

from collections.abc import Sequence

from alembic import op

revision: str = "20260815_0009"
down_revision: str | None = "20260813_0008"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Remove índices redundantes e mantém restrições únicas nomeadas."""

    op.drop_index(
        "ix_companies_document",
        table_name="companies",
    )

    op.drop_index(
        "name",
        table_name="organizations",
    )
    op.drop_index(
        "ix_organizations_name",
        table_name="organizations",
    )
    op.create_unique_constraint(
        "uq_organizations_name",
        "organizations",
        ["name"],
    )


def downgrade() -> None:
    """Restaura os índices redundantes existentes anteriormente."""

    op.drop_constraint(
        "uq_organizations_name",
        "organizations",
        type_="unique",
    )
    op.create_unique_constraint(
        "name",
        "organizations",
        ["name"],
    )
    op.create_index(
        "ix_organizations_name",
        "organizations",
        ["name"],
        unique=True,
    )

    op.create_index(
        "ix_companies_document",
        "companies",
        ["document"],
        unique=False,
    )
