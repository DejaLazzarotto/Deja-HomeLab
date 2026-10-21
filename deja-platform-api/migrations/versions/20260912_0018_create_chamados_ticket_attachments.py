"""Cria os anexos dos chamados do Deja Chamados.

Revision ID: 20260912_0018
Revises: 20260910_0017
Create Date: 2026-09-12
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260912_0018"
down_revision: str | None = "20260910_0017"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Cria a tabela e os índices dos anexos dos chamados."""

    op.create_table(
        "chamados_ticket_attachments",
        sa.Column(
            "id",
            sa.String(length=36),
            nullable=False,
        ),
        sa.Column(
            "ticket_id",
            sa.String(length=36),
            nullable=False,
        ),
        sa.Column(
            "file_name",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "original_name",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "content_type",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "file_size",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "file_path",
            sa.String(length=500),
            nullable=False,
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
            name="fk_chamados_ticket_attachments_ticket_id",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["created_by_user_id"],
            ["users.id"],
            name="fk_chamados_ticket_attachments_created_by_user_id",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_chamados_ticket_attachments_ticket_id",
        "chamados_ticket_attachments",
        ["ticket_id"],
        unique=False,
    )
    op.create_index(
        "ix_chamados_ticket_attachments_created_by_user_id",
        "chamados_ticket_attachments",
        ["created_by_user_id"],
        unique=False,
    )
    op.create_index(
        "ix_chamados_ticket_attachments_created_at",
        "chamados_ticket_attachments",
        ["created_at"],
        unique=False,
    )


def downgrade() -> None:
    """Remove os anexos dos chamados."""

    op.drop_table(
        "chamados_ticket_attachments",
    )