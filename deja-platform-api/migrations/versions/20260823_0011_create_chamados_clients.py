"""Cria os clientes multi-organização do Deja Chamados.

Revision ID: 20260823_0011
Revises: 20260821_0010
Create Date: 2026-08-23
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260823_0011"
down_revision: str | None = "20260821_0010"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Cria a tabela de clientes do Deja Chamados."""

    op.create_table(
        "chamados_clients",
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
            "company_name",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "fantasy_name",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "document",
            sa.String(length=14),
            nullable=False,
        ),
        sa.Column(
            "contact_name",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "phone",
            sa.String(length=11),
            nullable=False,
        ),
        sa.Column(
            "whatsapp",
            sa.String(length=11),
            nullable=False,
        ),
        sa.Column(
            "email",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "city",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "state",
            sa.String(length=2),
            nullable=False,
        ),
        sa.Column(
            "notes",
            sa.Text(),
            nullable=False,
        ),
        sa.Column(
            "active",
            sa.Boolean(),
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
            server_default=sa.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            name="fk_chamados_clients_organization_id",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenants.id"],
            name="fk_chamados_clients_tenant_id",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["environment_id"],
            ["environments.id"],
            name="fk_chamados_clients_environment_id",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "organization_id",
            "document",
            name=("uq_chamados_clients_organization_document"),
        ),
    )

    op.create_index(
        "ix_chamados_clients_organization_id",
        "chamados_clients",
        ["organization_id"],
        unique=False,
    )
    op.create_index(
        "ix_chamados_clients_tenant_id",
        "chamados_clients",
        ["tenant_id"],
        unique=False,
    )
    op.create_index(
        "ix_chamados_clients_environment_id",
        "chamados_clients",
        ["environment_id"],
        unique=False,
    )


def downgrade() -> None:
    """Remove a tabela de clientes do Deja Chamados."""

    op.drop_index(
        "ix_chamados_clients_environment_id",
        table_name="chamados_clients",
    )
    op.drop_index(
        "ix_chamados_clients_tenant_id",
        table_name="chamados_clients",
    )
    op.drop_index(
        "ix_chamados_clients_organization_id",
        table_name="chamados_clients",
    )
    op.drop_table("chamados_clients")
