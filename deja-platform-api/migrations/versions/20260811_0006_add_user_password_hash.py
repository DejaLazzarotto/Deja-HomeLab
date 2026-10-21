"""Adiciona credencial de senha aos usuários.

Revision ID: 20260811_0006
Revises: 20260811_0005
Create Date: 2026-08-11
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260811_0006"
down_revision: str | None = "20260811_0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Adiciona o hash opcional da senha aos usuários."""

    op.add_column(
        "users",
        sa.Column(
            "password_hash",
            sa.String(length=255),
            nullable=True,
        ),
    )


def downgrade() -> None:
    """Remove o hash da senha dos usuários."""

    op.drop_column("users", "password_hash")