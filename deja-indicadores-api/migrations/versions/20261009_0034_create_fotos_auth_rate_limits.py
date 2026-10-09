"""Cria contadores de requisicoes para autenticacao do Fotos PWA.

Revision ID: 20261009_0034
Revises: 20261009_0033
Create Date: 2026-10-09
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20261009_0034"
down_revision: str | None = "20261009_0033"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Cria tabela de limitacao de requisicoes."""

    op.create_table(
        "fotos_auth_rate_limits",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("scope", sa.String(16), nullable=False),
        sa.Column("subject_hash", sa.String(64), nullable=False),
        sa.Column("window_start", sa.DateTime(), nullable=False),
        sa.Column(
            "request_count",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.PrimaryKeyConstraint(
            "id",
            name="pk_fotos_auth_rate_limits",
        ),
        sa.UniqueConstraint(
            "scope",
            "subject_hash",
            "window_start",
            name="uq_fotos_auth_rate_limits_window",
        ),
        sa.CheckConstraint(
            "scope IN ('ip', 'account')",
            name="ck_fotos_auth_rate_limits_scope",
        ),
        sa.CheckConstraint(
            "request_count >= 0",
            name="ck_fotos_auth_rate_limits_count",
        ),
    )

    op.create_index(
        "ix_fotos_auth_rate_limits_window_start",
        "fotos_auth_rate_limits",
        ["window_start"],
        unique=False,
    )


def downgrade() -> None:
    """Remove tabela de limitacao de requisicoes."""

    op.drop_index(
        "ix_fotos_auth_rate_limits_window_start",
        table_name="fotos_auth_rate_limits",
    )

    op.drop_table("fotos_auth_rate_limits")
