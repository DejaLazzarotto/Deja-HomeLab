"""Cria a tabela de álbuns do Deja Fotos.

Revision ID: 20260914_0020
Revises: 20260914_0019
Create Date: 2026-09-14
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "20260914_0020"
down_revision: str | None = "20260914_0019"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Cria a estrutura comercial de álbuns do Deja Fotos."""

    op.create_table(
        "fotos_albums",
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
            "name",
            sa.String(length=150),
            nullable=False,
        ),
        sa.Column(
            "description",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
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
            name="fk_fotos_albums_organization_id",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenants.id"],
            name="fk_fotos_albums_tenant_id",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["environment_id"],
            ["environments.id"],
            name="fk_fotos_albums_environment_id",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint(
            "id",
            name="pk_fotos_albums",
        ),
        sa.UniqueConstraint(
            "organization_id",
            "tenant_id",
            "environment_id",
            "name",
            name="uq_fotos_albums_scope_name",
        ),
    )

    op.create_index(
        "ix_fotos_albums_organization_id",
        "fotos_albums",
        ["organization_id"],
        unique=False,
    )

    op.create_index(
        "ix_fotos_albums_tenant_id",
        "fotos_albums",
        ["tenant_id"],
        unique=False,
    )

    op.create_index(
        "ix_fotos_albums_environment_id",
        "fotos_albums",
        ["environment_id"],
        unique=False,
    )


def downgrade() -> None:
    """Remove a tabela de álbuns do Deja Fotos."""

    op.drop_index(
        "ix_fotos_albums_environment_id",
        table_name="fotos_albums",
    )

    op.drop_index(
        "ix_fotos_albums_tenant_id",
        table_name="fotos_albums",
    )

    op.drop_index(
        "ix_fotos_albums_organization_id",
        table_name="fotos_albums",
    )

    op.drop_table("fotos_albums")