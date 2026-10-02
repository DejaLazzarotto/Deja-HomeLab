"""Adiciona papel institucional neutro para usuários comuns.

Revision ID: 20261002_0031
Revises: 20261001_0030
Create Date: 2026-10-02
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20261002_0031"
down_revision: str | None = "20261001_0030"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


PREVIOUS_USER_ROLE = sa.Enum(
    "platform_admin",
    "organization_admin",
    "tenant_admin",
    "manager",
    "analyst",
    "viewer",
    "client",
    name="user_role",
)

NEUTRAL_USER_ROLE = sa.Enum(
    "platform_admin",
    "organization_admin",
    "tenant_admin",
    "manager",
    "analyst",
    "viewer",
    "client",
    "user",
    name="user_role",
)


def upgrade() -> None:
    """Permite usuários institucionais sem papel funcional global."""

    op.alter_column(
        "users",
        "role",
        existing_type=PREVIOUS_USER_ROLE,
        type_=NEUTRAL_USER_ROLE,
        existing_nullable=False,
    )


def downgrade() -> None:
    """Remove o papel neutro quando não estiver em uso."""

    connection = op.get_bind()

    neutral_user_count = connection.scalar(
        sa.text(
            """
            SELECT COUNT(*)
            FROM users
            WHERE role = 'user'
            """
        )
    )

    if neutral_user_count:
        raise RuntimeError(
            "Não é possível remover o papel user enquanto "
            "existirem usuários com esse papel."
        )

    op.alter_column(
        "users",
        "role",
        existing_type=NEUTRAL_USER_ROLE,
        type_=PREVIOUS_USER_ROLE,
        existing_nullable=False,
    )