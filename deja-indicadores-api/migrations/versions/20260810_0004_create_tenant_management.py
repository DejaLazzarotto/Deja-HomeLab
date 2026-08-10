"""Cria as tabelas do Tenant Management.

Revision ID: 20260810_0004
Revises: 20260810_0003
Create Date: 2026-08-10
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "20260810_0004"
down_revision: str | None = "20260810_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Cria organizações, tenants e ambientes."""

    organization_status = sa.Enum(
        "provisioning",
        "active",
        "inactive",
        name="organization_status",
    )
    tenant_status = sa.Enum(
        "provisioning",
        "active",
        "inactive",
        name="tenant_status",
    )
    environment_status = sa.Enum(
        "provisioning",
        "active",
        "inactive",
        name="environment_status",
    )

    op.create_table(
        "organizations",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column(
            "status",
            organization_status,
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text(
                "CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"
            ),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.create_index(
        "ix_organizations_name",
        "organizations",
        ["name"],
        unique=True,
    )

    op.create_table(
        "tenants",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column(
            "organization_id",
            sa.String(length=36),
            nullable=False,
        ),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column(
            "status",
            tenant_status,
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text(
                "CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"
            ),
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            name="fk_tenants_organization_id",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "organization_id",
            "name",
            name="uq_tenants_organization_name",
        ),
    )

    op.create_index(
        "ix_tenants_organization_id",
        "tenants",
        ["organization_id"],
        unique=False,
    )

    op.create_table(
        "environments",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column(
            "tenant_id",
            sa.String(length=36),
            nullable=False,
        ),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column(
            "status",
            environment_status,
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text(
                "CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"
            ),
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenants.id"],
            name="fk_environments_tenant_id",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "tenant_id",
            "name",
            name="uq_environments_tenant_name",
        ),
    )

    op.create_index(
        "ix_environments_tenant_id",
        "environments",
        ["tenant_id"],
        unique=False,
    )


def downgrade() -> None:
    """Remove ambientes, tenants e organizações."""

    op.drop_index(
        "ix_environments_tenant_id",
        table_name="environments",
    )
    op.drop_table("environments")

    op.drop_index(
        "ix_tenants_organization_id",
        table_name="tenants",
    )
    op.drop_table("tenants")

    op.drop_index(
        "ix_organizations_name",
        table_name="organizations",
    )
    op.drop_table("organizations")