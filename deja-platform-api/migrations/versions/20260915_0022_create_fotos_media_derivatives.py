"""Cria a tabela de derivados de mídias do Deja Fotos.

Revision ID: 20260915_0022
Revises: 20260915_0021
Create Date: 2026-09-15
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260915_0022"
down_revision: str | None = "20260915_0021"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Cria a estrutura de derivados de mídias do Deja Fotos."""

    op.create_table(
        "fotos_media_derivatives",
        sa.Column(
            "id",
            sa.String(length=36),
            nullable=False,
        ),
        sa.Column(
            "media_id",
            sa.String(length=36),
            nullable=False,
        ),
        sa.Column(
            "derivative_type",
            sa.String(length=30),
            nullable=False,
        ),
        sa.Column(
            "storage_key",
            sa.String(length=512),
            nullable=False,
        ),
        sa.Column(
            "content_type",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "file_extension",
            sa.String(length=20),
            nullable=True,
        ),
        sa.Column(
            "file_size",
            sa.BigInteger(),
            nullable=False,
        ),
        sa.Column(
            "width",
            sa.Integer(),
            nullable=True,
        ),
        sa.Column(
            "height",
            sa.Integer(),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(
            ["media_id"],
            ["fotos_media.id"],
            name="fk_fotos_media_derivatives_media_id",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "id",
            name="pk_fotos_media_derivatives",
        ),
        sa.UniqueConstraint(
            "media_id",
            "derivative_type",
            name="uq_fotos_media_derivatives_media_type",
        ),
        sa.UniqueConstraint(
            "storage_key",
            name="uq_fotos_media_derivatives_storage_key",
        ),
    )

    op.create_index(
        "ix_fotos_media_derivatives_media_id",
        "fotos_media_derivatives",
        ["media_id"],
        unique=False,
    )

    op.create_index(
        "ix_fotos_media_derivatives_derivative_type",
        "fotos_media_derivatives",
        ["derivative_type"],
        unique=False,
    )

    op.create_index(
        "ix_fotos_media_derivatives_created_at",
        "fotos_media_derivatives",
        ["created_at"],
        unique=False,
    )


def downgrade() -> None:
    """Remove a tabela de derivados de mídias do Deja Fotos."""

    op.drop_index(
        "ix_fotos_media_derivatives_created_at",
        table_name="fotos_media_derivatives",
    )

    op.drop_index(
        "ix_fotos_media_derivatives_derivative_type",
        table_name="fotos_media_derivatives",
    )

    op.drop_index(
        "ix_fotos_media_derivatives_media_id",
        table_name="fotos_media_derivatives",
    )

    op.drop_table(
        "fotos_media_derivatives",
    )