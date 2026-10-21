"""Cria favoritos individuais de mídias do Deja Fotos.

Revision ID: 20261013_0036
Revises: 20261009_0035
Create Date: 2026-10-13
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20261013_0036"
down_revision: str | None = "20261009_0035"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Cria a tabela de favoritos individuais."""

    op.create_table(
        "fotos_media_favorites",
        sa.Column(
            "id",
            sa.String(length=36),
            primary_key=True,
        ),
        sa.Column(
            "user_id",
            sa.String(length=36),
            nullable=False,
        ),
        sa.Column(
            "media_id",
            sa.String(length=36),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_fotos_media_favorites_user_id",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["media_id"],
            ["fotos_media.id"],
            name="fk_fotos_media_favorites_media_id",
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint(
            "user_id",
            "media_id",
            name="uq_fotos_media_favorites_user_media",
        ),
    )

    op.create_index(
        "ix_fotos_media_favorites_media_id",
        "fotos_media_favorites",
        ["media_id"],
    )


def downgrade() -> None:
    """Remove a tabela de favoritos."""

    op.drop_index(
        "ix_fotos_media_favorites_media_id",
        table_name="fotos_media_favorites",
    )

    op.drop_table("fotos_media_favorites")