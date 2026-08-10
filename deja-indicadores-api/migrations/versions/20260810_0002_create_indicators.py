"""Cria a tabela de indicadores.

Revision ID: 20260810_0002
Revises: 20260809_0001
Create Date: 2026-08-10
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260810_0002"
down_revision: str | None = "20260809_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Cria a estrutura persistente de indicadores."""

    op.create_table(
        "indicators",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("company_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("unit", sa.String(length=50), nullable=False),
        sa.Column(
            "direction",
            sa.Enum(
                "higher_is_better",
                "lower_is_better",
                name="indicator_direction",
            ),
            nullable=False,
        ),
        sa.Column(
            "target_value",
            sa.Numeric(precision=18, scale=4),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum(
                "active",
                "inactive",
                name="indicator_status",
            ),
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
        sa.ForeignKeyConstraint(
            ["company_id"],
            ["companies.id"],
            name="fk_indicators_company_id",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "company_id",
            "name",
            name="uq_indicators_company_name",
        ),
    )

    op.create_index(
        "ix_indicators_company_id",
        "indicators",
        ["company_id"],
        unique=False,
    )


def downgrade() -> None:
    """Remove a estrutura persistente de indicadores."""

    op.drop_index(
        "ix_indicators_company_id",
        table_name="indicators",
    )
    op.drop_table("indicators")