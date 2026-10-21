"""Adiciona metadados da fonte e rastreabilidade de data às mídias.

Revision ID: 20260916_0023
Revises: 20260915_0022
Create Date: 2026-09-16
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260916_0023"
down_revision: str | None = "20260915_0022"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Adiciona os metadados da fonte e da classificação de data."""

    op.add_column(
        "fotos_media",
        sa.Column(
            "source_content_type",
            sa.String(length=255),
            nullable=True,
        ),
    )

    op.add_column(
        "fotos_media",
        sa.Column(
            "source_file_extension",
            sa.String(length=20),
            nullable=True,
        ),
    )

    op.add_column(
        "fotos_media",
        sa.Column(
            "source_file_size",
            sa.BigInteger(),
            nullable=True,
        ),
    )

    op.add_column(
        "fotos_media",
        sa.Column(
            "source_checksum_sha256",
            sa.String(length=64),
            nullable=True,
        ),
    )

    op.add_column(
        "fotos_media",
        sa.Column(
            "was_converted",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )

    op.add_column(
        "fotos_media",
        sa.Column(
            "original_date_source",
            sa.String(length=30),
            nullable=True,
        ),
    )

    op.add_column(
        "fotos_media",
        sa.Column(
            "original_date_verified",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )

    op.add_column(
        "fotos_media",
        sa.Column(
            "original_date_conflict",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )

    op.execute(
        sa.text(
            """
            UPDATE fotos_media
            SET
                source_content_type = content_type,
                source_file_extension = file_extension,
                source_file_size = file_size,
                source_checksum_sha256 = checksum_sha256,
                was_converted = false,
                original_date_source = CASE
                    WHEN original_date IS NULL THEN NULL
                    ELSE 'embedded_metadata'
                END,
                original_date_verified = false,
                original_date_conflict = false
            """
        )
    )

    op.alter_column(
        "fotos_media",
        "source_content_type",
        existing_type=sa.String(length=255),
        nullable=False,
    )

    op.alter_column(
        "fotos_media",
        "source_file_size",
        existing_type=sa.BigInteger(),
        nullable=False,
    )

    op.alter_column(
        "fotos_media",
        "source_checksum_sha256",
        existing_type=sa.String(length=64),
        nullable=False,
    )

    op.create_index(
        "ix_fotos_media_source_checksum_sha256",
        "fotos_media",
        ["source_checksum_sha256"],
        unique=False,
    )


def downgrade() -> None:
    """Remove os metadados da fonte e da classificação de data."""

    op.drop_index(
        "ix_fotos_media_source_checksum_sha256",
        table_name="fotos_media",
    )

    op.drop_column(
        "fotos_media",
        "original_date_conflict",
    )

    op.drop_column(
        "fotos_media",
        "original_date_verified",
    )

    op.drop_column(
        "fotos_media",
        "original_date_source",
    )

    op.drop_column(
        "fotos_media",
        "was_converted",
    )

    op.drop_column(
        "fotos_media",
        "source_checksum_sha256",
    )

    op.drop_column(
        "fotos_media",
        "source_file_size",
    )

    op.drop_column(
        "fotos_media",
        "source_file_extension",
    )

    op.drop_column(
        "fotos_media",
        "source_content_type",
    )