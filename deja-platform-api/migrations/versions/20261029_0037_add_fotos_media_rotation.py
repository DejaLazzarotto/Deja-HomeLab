"""add fotos media rotation

Revision ID: 20261029_0037
Revises: 08453cc623c8
Create Date: 2026-10-29
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20261029_0037"
down_revision: str | None = "08453cc623c8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Adiciona a orientação persistente das fotografias."""

    op.add_column(
        "fotos_media",
        sa.Column(
            "rotation_degrees",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
    )


def downgrade() -> None:
    """Remove a orientação persistente das fotografias."""

    op.drop_column("fotos_media", "rotation_degrees")
