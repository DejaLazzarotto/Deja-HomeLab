"""Adiciona a precisão da data original das mídias.

Revision ID: 20260918_0025
Revises: 20260916_0024
Create Date: 2026-09-18
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260918_0025"
down_revision: str | None = "20260916_0024"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Registra se a data possui ou não um horário conhecido."""

    op.add_column(
        "fotos_media",
        sa.Column(
            "original_date_precision",
            sa.String(length=20),
            nullable=True,
        ),
    )

    op.execute(
        sa.text(
            """
            UPDATE fotos_media
            SET original_date_precision = 'datetime'
            WHERE original_date IS NOT NULL
            """
        )
    )


def downgrade() -> None:
    """Remove a precisão da data original."""

    op.drop_column(
        "fotos_media",
        "original_date_precision",
    )
