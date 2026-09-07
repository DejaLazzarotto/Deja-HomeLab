"""Cria o histórico de eventos dos chamados do Deja Chamados.

Revision ID: 20260907_0015
Revises: 20260828_0014
Create Date: 2026-09-07
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260907_0015"
down_revision: str | None = "20260828_0014"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Cria a tabela e os índices do histórico dos chamados."""

    op.create_table(
        "chamados_ticket_timeline",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("ticket_id", sa.String(length=36), nullable=False),
        sa.Column("event_type", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("previous_value", sa.Text(), nullable=True),
        sa.Column("new_value", sa.Text(), nullable=True),
        sa.Column("created_by_user_id", sa.String(length=36), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["ticket_id"],
            ["chamados_tickets.id"],
            name="fk_chamados_ticket_timeline_ticket_id",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["created_by_user_id"],
            ["users.id"],
            name="fk_chamados_ticket_timeline_created_by_user_id",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_chamados_ticket_timeline_ticket_id",
        "chamados_ticket_timeline",
        ["ticket_id"],
        unique=False,
    )
    op.create_index(
        "ix_chamados_ticket_timeline_event_type",
        "chamados_ticket_timeline",
        ["event_type"],
        unique=False,
    )
    op.create_index(
        "ix_chamados_ticket_timeline_created_by_user_id",
        "chamados_ticket_timeline",
        ["created_by_user_id"],
        unique=False,
    )
    op.create_index(
        "ix_chamados_ticket_timeline_created_at",
        "chamados_ticket_timeline",
        ["created_at"],
        unique=False,
    )


def downgrade() -> None:
    """Remove o histórico de eventos dos chamados."""

    op.drop_table("chamados_ticket_timeline")
