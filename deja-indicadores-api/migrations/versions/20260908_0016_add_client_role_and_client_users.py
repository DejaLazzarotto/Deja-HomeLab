"""Adiciona papel client e vínculo entre usuários e Clientes do Chamados.

Revision ID: 20260908_0016
Revises: 20260907_0015
Create Date: 2026-09-08
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260908_0016"
down_revision: str | None = "20260907_0015"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


PREVIOUS_USER_ROLE = sa.Enum(
    "platform_admin",
    "organization_admin",
    "tenant_admin",
    "manager",
    "analyst",
    "viewer",
    name="user_role",
)

PORTAL_USER_ROLE = sa.Enum(
    "platform_admin",
    "organization_admin",
    "tenant_admin",
    "manager",
    "analyst",
    "viewer",
    "client",
    name="user_role",
)


def upgrade() -> None:
    """Permite usuários externos vinculados a Clientes do Chamados."""

    op.alter_column(
        "users",
        "role",
        existing_type=PREVIOUS_USER_ROLE,
        type_=PORTAL_USER_ROLE,
        existing_nullable=False,
    )

    op.create_table(
        "chamados_client_users",
        sa.Column(
            "id",
            sa.String(length=36),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.String(length=36),
            nullable=False,
        ),
        sa.Column(
            "client_id",
            sa.String(length=36),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_chamados_client_users_user_id",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["client_id"],
            ["chamados_clients.id"],
            name="fk_chamados_client_users_client_id",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id",
            name="uq_chamados_client_users_user_id",
        ),
    )

    op.create_index(
        "ix_chamados_client_users_user_id",
        "chamados_client_users",
        ["user_id"],
        unique=False,
    )

    op.create_index(
        "ix_chamados_client_users_client_id",
        "chamados_client_users",
        ["client_id"],
        unique=False,
    )


def downgrade() -> None:
    """Remove o vínculo de Portal e o papel client quando não estiver em uso."""

    connection = op.get_bind()

    client_user_count = connection.scalar(
        sa.text(
            """
            SELECT COUNT(*)
            FROM users
            WHERE role = 'client'
            """
        )
    )

    if client_user_count:
        raise RuntimeError(
            "Não é possível remover o papel client enquanto "
            "existirem usuários com esse papel."
        )

    op.drop_index(
        "ix_chamados_client_users_client_id",
        table_name="chamados_client_users",
    )

    op.drop_index(
        "ix_chamados_client_users_user_id",
        table_name="chamados_client_users",
    )

    op.drop_table("chamados_client_users")

    op.alter_column(
        "users",
        "role",
        existing_type=PORTAL_USER_ROLE,
        type_=PREVIOUS_USER_ROLE,
        existing_nullable=False,
    )