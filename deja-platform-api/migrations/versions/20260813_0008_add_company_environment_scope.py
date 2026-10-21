"""Adiciona o escopo institucional de ambiente às empresas.

Revision ID: 20260813_0008
Revises: 20260812_0007
Create Date: 2026-08-13
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260813_0008"
down_revision: str | None = "20260812_0007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Vincula obrigatoriamente cada empresa a um ambiente."""

    connection = op.get_bind()
    company_count = connection.scalar(sa.text("""
            SELECT COUNT(*)
            FROM companies
            """))

    if company_count:
        raise RuntimeError(
            "Não é possível adicionar o escopo institucional enquanto "
            "existirem empresas sem ambiente associado."
        )

    op.add_column(
        "companies",
        sa.Column(
            "environment_id",
            sa.String(length=36),
            nullable=False,
        ),
    )
    op.create_foreign_key(
        "fk_companies_environment_id",
        "companies",
        "environments",
        ["environment_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_index(
        "ix_companies_environment_id",
        "companies",
        ["environment_id"],
        unique=False,
    )


def downgrade() -> None:
    """Remove o vínculo institucional das empresas."""

    connection = op.get_bind()
    company_count = connection.scalar(sa.text("""
            SELECT COUNT(*)
            FROM companies
            """))

    if company_count:
        raise RuntimeError(
            "Não é possível remover o escopo institucional enquanto "
            "existirem empresas cadastradas."
        )

    op.drop_index(
        "ix_companies_environment_id",
        table_name="companies",
    )
    op.drop_constraint(
        "fk_companies_environment_id",
        "companies",
        type_="foreignkey",
    )
    op.drop_column("companies", "environment_id")
