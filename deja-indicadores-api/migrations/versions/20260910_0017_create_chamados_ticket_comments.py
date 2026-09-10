"""Cria os comentários dos chamados do Deja Chamados.

Revision ID: 20260910_0017
Revises: 20260908_0016
Create Date: 2026-09-10
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "20260910_0017"
down_revision: str | None = "20260908_0016"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Cria a tabela e os índices dos comentários dos chamados."""

    op.create_table(
        "chamados_ticket_comments",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("ticket_id", sa.String(length=36), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column(
            "visibility",
            sa.Enum(
                "public",
                "internal",
                name="chamados_ticket_comment_visibility",
            ),
            nullable=False,
            server_default="public",
        ),
        sa.Column(
            "created_by_user_id",
            sa.String(length=36),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["ticket_id"],
            ["chamados_tickets.id"],
            name="fk_chamados_ticket_comments_ticket_id",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["created_by_user_id"],
            ["users.id"],
            name="fk_chamados_ticket_comments_created_by_user_id",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_chamados_ticket_comments_ticket_id",
        "chamados_ticket_comments",
        ["ticket_id"],
        unique=False,
    )
    op.create_index(
        "ix_chamados_ticket_comments_visibility",
        "chamados_ticket_comments",
        ["visibility"],
        unique=False,
    )
    op.create_index(
        "ix_chamados_ticket_comments_created_by_user_id",
        "chamados_ticket_comments",
        ["created_by_user_id"],
        unique=False,
    )
    op.create_index(
        "ix_chamados_ticket_comments_created_at",
        "chamados_ticket_comments",
        ["created_at"],
        unique=False,
    )


def downgrade() -> None:
    """Remove os comentários dos chamados."""

    op.drop_table("chamados_ticket_comments")