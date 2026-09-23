"""Cria pessoas e vínculos manuais com mídias do Deja Fotos.

Revision ID: 20260923_0027
Revises: 20260921_0026
Create Date: 2026-09-23
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260923_0027"
down_revision: str | None = "20260921_0026"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Cria pessoas e seus vínculos com mídias no mesmo escopo."""

    op.create_table(
        "fotos_people",
        sa.Column("id", sa.String(length=36), nullable=False),
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
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
        sa.Column(
            "avatar_storage_key",
            sa.String(length=512),
            nullable=True,
        ),
        sa.Column(
            "avatar_content_type",
            sa.String(length=100),
            nullable=True,
        ),
        sa.Column(
            "avatar_file_size",
            sa.BigInteger(),
            nullable=True,
        ),
        sa.Column(
            "avatar_checksum_sha256",
            sa.String(length=64),
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
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            name="fk_fotos_people_organization_id",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenants.id"],
            name="fk_fotos_people_tenant_id",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["environment_id"],
            ["environments.id"],
            name="fk_fotos_people_environment_id",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_fotos_people"),
        sa.UniqueConstraint(
            "organization_id",
            "tenant_id",
            "environment_id",
            "name",
            name="uq_fotos_people_scope_name",
        ),
        sa.UniqueConstraint(
            "avatar_storage_key",
            name="uq_fotos_people_avatar_storage_key",
        ),
    )

    for column in (
        "organization_id",
        "tenant_id",
        "environment_id",
    ):
        op.create_index(
            f"ix_fotos_people_{column}",
            "fotos_people",
            [column],
        )

    op.create_table(
        "fotos_person_media",
        sa.Column(
            "person_id",
            sa.String(length=36),
            nullable=False,
        ),
        sa.Column(
            "media_id",
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
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(
            ["person_id"],
            ["fotos_people.id"],
            name="fk_fotos_person_media_person_id",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["media_id"],
            ["fotos_media.id"],
            name="fk_fotos_person_media_media_id",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            name="fk_fotos_person_media_organization_id",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenants.id"],
            name="fk_fotos_person_media_tenant_id",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["environment_id"],
            ["environments.id"],
            name="fk_fotos_person_media_environment_id",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint(
            "person_id",
            "media_id",
            name="pk_fotos_person_media",
        ),
    )

    op.create_index(
        "ix_fotos_person_media_media_id",
        "fotos_person_media",
        ["media_id"],
    )


def downgrade() -> None:
    """Remove vínculos e pessoas do Deja Fotos."""

    op.drop_index(
        "ix_fotos_person_media_media_id",
        table_name="fotos_person_media",
    )
    op.drop_table("fotos_person_media")

    for column in (
        "environment_id",
        "tenant_id",
        "organization_id",
    ):
        op.drop_index(
            f"ix_fotos_people_{column}",
            table_name="fotos_people",
        )

    op.drop_table("fotos_people")