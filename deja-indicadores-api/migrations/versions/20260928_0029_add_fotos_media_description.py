"""Descrição editável das mídias de vídeo.

Revision ID: 20260928_0029
Revises: 20260924_0028
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260928_0029"
down_revision: str | None = "20260924_0028"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "fotos_media",
        sa.Column(
            "description",
            sa.Text(),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column(
        "fotos_media",
        "description",
    )
