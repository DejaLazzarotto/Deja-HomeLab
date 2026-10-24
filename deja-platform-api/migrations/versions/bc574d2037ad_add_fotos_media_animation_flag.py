"""add fotos media animation flag

Revision ID: bc574d2037ad
Revises: a6d1f413a692
Create Date: 2026-10-24 19:21:35.030072
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = 'bc574d2037ad'
down_revision: str | None = 'a6d1f413a692'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Adiciona a identificação de imagens animadas."""

    op.add_column(
        "fotos_media",
        sa.Column(
            "is_animated",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )


def downgrade() -> None:
    """Remove a identificação de imagens animadas."""

    op.drop_column(
        "fotos_media",
        "is_animated",
    )