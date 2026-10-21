"""Garante unicidade da fonte de mídia por ambiente.

Revision ID: 20260916_0024
Revises: 20260916_0023
Create Date: 2026-09-16
"""

from collections.abc import Sequence

from alembic import op

revision: str = "20260916_0024"
down_revision: str | None = "20260916_0023"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Impede fontes duplicadas dentro do mesmo ambiente."""

    op.create_unique_constraint(
        "uq_fotos_media_environment_source_checksum",
        "fotos_media",
        [
            "environment_id",
            "source_checksum_sha256",
        ],
    )


def downgrade() -> None:
    """Remove a unicidade da fonte por ambiente."""

    op.drop_constraint(
        "uq_fotos_media_environment_source_checksum",
        "fotos_media",
        type_="unique",
    )