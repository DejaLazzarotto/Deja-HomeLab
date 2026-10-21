"""Cria as descrições mensais dos álbuns do Deja Fotos.

Revision ID: 20260921_0026
Revises: 20260918_0025
Create Date: 2026-09-21
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260921_0026"
down_revision: str | None = "20260918_0025"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Cria descrições próprias para cada álbum, ano e mês."""

    op.create_table(
        "fotos_album_period_descriptions",
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
            nullable=False,
        ),
        sa.Column(
            "original_year",
            sa.SmallInteger(),
            nullable=False,
        ),
        sa.Column(
            "original_month",
            sa.SmallInteger(),
            nullable=False,
        ),
        sa.Column(
            "description",
            sa.Text(),
            nullable=False,
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
        sa.CheckConstraint(
            "original_month >= 1 AND original_month <= 12",
            name="ck_fotos_album_period_descriptions_month",
        ),
        sa.CheckConstraint(
            "original_year >= 1 AND original_year <= 9999",
            name="ck_fotos_album_period_descriptions_year",
        ),
        sa.ForeignKeyConstraint(
            ["album_id"],
            ["fotos_albums.id"],
            name="fk_fotos_album_period_descriptions_album_id",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["environment_id"],
            ["environments.id"],
            name=(
                "fk_fotos_album_period_descriptions_"
                "environment_id"
            ),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            name=(
                "fk_fotos_album_period_descriptions_"
                "organization_id"
            ),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenants.id"],
            name="fk_fotos_album_period_descriptions_tenant_id",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint(
            "id",
            name="pk_fotos_album_period_descriptions",
        ),
        sa.UniqueConstraint(
            "album_id",
            "original_year",
            "original_month",
            name="uq_fotos_album_period_descriptions_period",
        ),
    )

    op.create_index(
        "ix_fotos_album_period_descriptions_album_id",
        "fotos_album_period_descriptions",
        ["album_id"],
        unique=False,
    )

    op.create_index(
        "ix_fotos_album_period_descriptions_environment_id",
        "fotos_album_period_descriptions",
        ["environment_id"],
        unique=False,
    )

    op.create_index(
        "ix_fotos_album_period_descriptions_organization_id",
        "fotos_album_period_descriptions",
        ["organization_id"],
        unique=False,
    )

    op.create_index(
        "ix_fotos_album_period_descriptions_tenant_id",
        "fotos_album_period_descriptions",
        ["tenant_id"],
        unique=False,
    )


def downgrade() -> None:
    """Remove as descrições mensais dos álbuns."""

    op.drop_index(
        "ix_fotos_album_period_descriptions_tenant_id",
        table_name="fotos_album_period_descriptions",
    )

    op.drop_index(
        "ix_fotos_album_period_descriptions_organization_id",
        table_name="fotos_album_period_descriptions",
    )

    op.drop_index(
        "ix_fotos_album_period_descriptions_environment_id",
        table_name="fotos_album_period_descriptions",
    )

    op.drop_index(
        "ix_fotos_album_period_descriptions_album_id",
        table_name="fotos_album_period_descriptions",
    )

    op.drop_table("fotos_album_period_descriptions")