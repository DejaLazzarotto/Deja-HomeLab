"""Cria a tabela de medições.

Revision ID: 20260810_0003
Revises: 20260810_0002
Create Date: 2026-08-10
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260810_0003"
down_revision: str | None = "20260810_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Cria a estrutura persistente de medições."""

    op.create_table(
        "measurements",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("indicator_id", sa.String(length=36), nullable=False),
        sa.Column("reference_date", sa.Date(), nullable=False),
        sa.Column(
            "actual_value",
            sa.Numeric(precision=18, scale=4),
            nullable=False,
        ),
        sa.Column("observation", sa.Text(), nullable=True),
        sa.Column("created_by", sa.String(length=36), nullable=True),
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
            ["indicator_id"],
            ["indicators.id"],
            name="fk_measurements_indicator_id",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "indicator_id",
            "reference_date",
            name="uq_measurements_indicator_reference_date",
        ),
    )

    op.create_index(
        "ix_measurements_indicator_id",
        "measurements",
        ["indicator_id"],
        unique=False,
    )
    op.create_index(
        "ix_measurements_reference_date",
        "measurements",
        ["reference_date"],
        unique=False,
    )


def downgrade() -> None:
    """Remove a estrutura persistente de medições."""

    op.drop_index(
        "ix_measurements_reference_date",
        table_name="measurements",
    )
    op.drop_index(
        "ix_measurements_indicator_id",
        table_name="measurements",
    )
    op.drop_table("measurements")