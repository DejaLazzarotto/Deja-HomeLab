"""Cria codigos de verificacao do Fotos PWA.

Revision ID: 20261009_0032
Revises: 20261002_0031
Create Date: 2026-10-09
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20261009_0032"
down_revision: str | None = "20261002_0031"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Cria a tabela de codigos temporarios."""

    op.create_table(
        "fotos_verification_codes",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column("purpose", sa.String(32), nullable=False),
        sa.Column("code_hash", sa.String(64), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column(
            "attempts",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.Column("consumed_at", sa.DateTime(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_fotos_verification_codes_user_id",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "id",
            name="pk_fotos_verification_codes",
        ),
        sa.CheckConstraint(
            "attempts >= 0",
            name="ck_fotos_verification_codes_attempts",
        ),
        sa.CheckConstraint(
            "purpose IN ('activation', 'password_reset')",
            name="ck_fotos_verification_codes_purpose",
        ),
    )

    op.create_index(
        "ix_fotos_verification_codes_user_purpose",
        "fotos_verification_codes",
        ["user_id", "purpose"],
        unique=False,
    )

    op.create_index(
        "ix_fotos_verification_codes_expires_at",
        "fotos_verification_codes",
        ["expires_at"],
        unique=False,
    )


def downgrade() -> None:
    """Remove a tabela de codigos temporarios."""

    op.drop_index(
        "ix_fotos_verification_codes_expires_at",
        table_name="fotos_verification_codes",
    )

    op.drop_index(
        "ix_fotos_verification_codes_user_purpose",
        table_name="fotos_verification_codes",
    )

    op.drop_table("fotos_verification_codes")