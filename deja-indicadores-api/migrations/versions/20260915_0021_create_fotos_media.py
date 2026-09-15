"""Cria a tabela de mídias do Deja Fotos.

Revision ID: 20260915_0021
Revises: 20260914_0020
Create Date: 2026-09-15
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260915_0021"
down_revision: str | None = "20260914_0020"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Cria a estrutura de mídias do Deja Fotos."""

    op.create_table(
        "fotos_media",
        sa.Column(
            "id",
            sa.String(length=36),
            nullable=False,
        ),
        sa.Column(
            "organization_id",
            sa.String(length=36),
            nullable=False,
        ),
        sa.Column(
            "tenant_id",
            sa.String(length=36),
            nullable=False,
        ),
        sa.Column(
            "environment_id",
            sa.String(length=36),
            nullable=False,
        ),
        sa.Column(
            "album_id",
            sa.String(length=36),
            nullable=True,
        ),
        sa.Column(
            "original_name",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "media_type",
            sa.String(length=20),
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
            "checksum_sha256",
            sa.String(length=64),
            nullable=False,
        ),
        sa.Column(
            "original_storage_key",
            sa.String(length=512),
            nullable=False,
        ),
        sa.Column(
            "processing_status",
            sa.String(length=30),
            nullable=False,
            server_default="received",
        ),
        sa.Column(
            "processing_error",
            sa.String(length=2000),
            nullable=True,
        ),
        sa.Column(
            "original_date",
            sa.DateTime(),
            nullable=True,
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
            "duration_seconds",
            sa.Float(),
            nullable=True,
        ),
        sa.Column(
            "view_count",
            sa.BigInteger(),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "created_by_user_id",
            sa.String(length=36),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "deleted_at",
            sa.DateTime(),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            name="fk_fotos_media_organization_id",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenants.id"],
            name="fk_fotos_media_tenant_id",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["environment_id"],
            ["environments.id"],
            name="fk_fotos_media_environment_id",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["album_id"],
            ["fotos_albums.id"],
            name="fk_fotos_media_album_id",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["created_by_user_id"],
            ["users.id"],
            name="fk_fotos_media_created_by_user_id",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint(
            "id",
            name="pk_fotos_media",
        ),
        sa.UniqueConstraint(
            "original_storage_key",
            name="uq_fotos_media_original_storage_key",
        ),
    )

    op.create_index(
        "ix_fotos_media_organization_id",
        "fotos_media",
        ["organization_id"],
        unique=False,
    )

    op.create_index(
        "ix_fotos_media_tenant_id",
        "fotos_media",
        ["tenant_id"],
        unique=False,
    )

    op.create_index(
        "ix_fotos_media_environment_id",
        "fotos_media",
        ["environment_id"],
        unique=False,
    )

    op.create_index(
        "ix_fotos_media_album_id",
        "fotos_media",
        ["album_id"],
        unique=False,
    )

    op.create_index(
        "ix_fotos_media_media_type",
        "fotos_media",
        ["media_type"],
        unique=False,
    )

    op.create_index(
        "ix_fotos_media_checksum_sha256",
        "fotos_media",
        ["checksum_sha256"],
        unique=False,
    )

    op.create_index(
        "ix_fotos_media_processing_status",
        "fotos_media",
        ["processing_status"],
        unique=False,
    )

    op.create_index(
        "ix_fotos_media_original_date",
        "fotos_media",
        ["original_date"],
        unique=False,
    )

    op.create_index(
        "ix_fotos_media_created_by_user_id",
        "fotos_media",
        ["created_by_user_id"],
        unique=False,
    )

    op.create_index(
        "ix_fotos_media_created_at",
        "fotos_media",
        ["created_at"],
        unique=False,
    )

    op.create_index(
        "ix_fotos_media_deleted_at",
        "fotos_media",
        ["deleted_at"],
        unique=False,
    )


def downgrade() -> None:
    """Remove a tabela de mídias do Deja Fotos."""

    op.drop_index(
        "ix_fotos_media_deleted_at",
        table_name="fotos_media",
    )

    op.drop_index(
        "ix_fotos_media_created_at",
        table_name="fotos_media",
    )

    op.drop_index(
        "ix_fotos_media_created_by_user_id",
        table_name="fotos_media",
    )

    op.drop_index(
        "ix_fotos_media_original_date",
        table_name="fotos_media",
    )

    op.drop_index(
        "ix_fotos_media_processing_status",
        table_name="fotos_media",
    )

    op.drop_index(
        "ix_fotos_media_checksum_sha256",
        table_name="fotos_media",
    )

    op.drop_index(
        "ix_fotos_media_media_type",
        table_name="fotos_media",
    )

    op.drop_index(
        "ix_fotos_media_album_id",
        table_name="fotos_media",
    )

    op.drop_index(
        "ix_fotos_media_environment_id",
        table_name="fotos_media",
    )

    op.drop_index(
        "ix_fotos_media_tenant_id",
        table_name="fotos_media",
    )

    op.drop_index(
        "ix_fotos_media_organization_id",
        table_name="fotos_media",
    )

    op.drop_table("fotos_media")