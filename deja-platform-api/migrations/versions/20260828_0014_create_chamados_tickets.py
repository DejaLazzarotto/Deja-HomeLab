"""Cria os chamados multi-organização do Deja Chamados.

Revision ID: 20260828_0014
Revises: 20260825_0013
Create Date: 2026-08-28
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260828_0014"
down_revision: str | None = "20260825_0013"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Cria a tabela e os índices dos chamados."""

    op.create_table(
        "chamados_tickets",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("organization_id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("environment_id", sa.String(length=36), nullable=False),
        sa.Column("client_id", sa.String(length=36), nullable=False),
        sa.Column("title", sa.String(length=150), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "open",
                "in_progress",
                "pending",
                "closed",
                name="chamados_ticket_status",
            ),
            nullable=False,
            server_default="open",
        ),
        sa.Column(
            "priority",
            sa.Enum(
                "low",
                "medium",
                "high",
                "critical",
                name="chamados_ticket_priority",
            ),
            nullable=False,
            server_default="medium",
        ),
        sa.Column("opened_by_user_id", sa.String(length=36), nullable=False),
        sa.Column("assigned_to_user_id", sa.String(length=36), nullable=True),
        sa.Column("closed_by_user_id", sa.String(length=36), nullable=True),
        sa.Column("closed_at", sa.DateTime(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            name="fk_chamados_tickets_organization_id",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenants.id"],
            name="fk_chamados_tickets_tenant_id",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["environment_id"],
            ["environments.id"],
            name="fk_chamados_tickets_environment_id",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["client_id"],
            ["chamados_clients.id"],
            name="fk_chamados_tickets_client_id",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["opened_by_user_id"],
            ["users.id"],
            name="fk_chamados_tickets_opened_by_user_id",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["assigned_to_user_id"],
            ["users.id"],
            name="fk_chamados_tickets_assigned_to_user_id",
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["closed_by_user_id"],
            ["users.id"],
            name="fk_chamados_tickets_closed_by_user_id",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_chamados_tickets_organization_id",
        "chamados_tickets",
        ["organization_id"],
        unique=False,
    )
    op.create_index(
        "ix_chamados_tickets_tenant_id",
        "chamados_tickets",
        ["tenant_id"],
        unique=False,
    )
    op.create_index(
        "ix_chamados_tickets_environment_id",
        "chamados_tickets",
        ["environment_id"],
        unique=False,
    )
    op.create_index(
        "ix_chamados_tickets_client_id",
        "chamados_tickets",
        ["client_id"],
        unique=False,
    )
    op.create_index(
        "ix_chamados_tickets_status",
        "chamados_tickets",
        ["status"],
        unique=False,
    )
    op.create_index(
        "ix_chamados_tickets_priority",
        "chamados_tickets",
        ["priority"],
        unique=False,
    )
    op.create_index(
        "ix_chamados_tickets_opened_by_user_id",
        "chamados_tickets",
        ["opened_by_user_id"],
        unique=False,
    )
    op.create_index(
        "ix_chamados_tickets_assigned_to_user_id",
        "chamados_tickets",
        ["assigned_to_user_id"],
        unique=False,
    )
    op.create_index(
        "ix_chamados_tickets_closed_by_user_id",
        "chamados_tickets",
        ["closed_by_user_id"],
        unique=False,
    )


def downgrade() -> None:
    """Remove a tabela de chamados."""

    op.drop_table("chamados_tickets")