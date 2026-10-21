"""Adiciona o papel administrativo global da plataforma.

Revision ID: 20260812_0007
Revises: 20260811_0006
Create Date: 2026-08-12
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260812_0007"
down_revision: str | None = "20260811_0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

PREVIOUS_USER_ROLE = sa.Enum(
    "organization_admin",
    "tenant_admin",
    "manager",
    "analyst",
    "viewer",
    name="user_role",
)

PLATFORM_USER_ROLE = sa.Enum(
    "platform_admin",
    "organization_admin",
    "tenant_admin",
    "manager",
    "analyst",
    "viewer",
    name="user_role",
)


def upgrade() -> None:
    """Permite identidades globais com o papel platform_admin."""

    op.alter_column(
        "users",
        "role",
        existing_type=PREVIOUS_USER_ROLE,
        type_=PLATFORM_USER_ROLE,
        existing_nullable=False,
    )
    op.alter_column(
        "users",
        "organization_id",
        existing_type=sa.String(length=36),
        nullable=True,
    )


def downgrade() -> None:
    """Remove o papel platform_admin quando não estiver em uso."""

    connection = op.get_bind()
    platform_admin_count = connection.scalar(
        sa.text(
            """
            SELECT COUNT(*)
            FROM users
            WHERE role = 'platform_admin'
            """
        )
    )

    if platform_admin_count:
        raise RuntimeError(
            "Não é possível remover platform_admin enquanto "
            "existirem usuários com esse papel."
        )

    op.alter_column(
        "users",
        "organization_id",
        existing_type=sa.String(length=36),
        nullable=False,
    )
    op.alter_column(
        "users",
        "role",
        existing_type=PLATFORM_USER_ROLE,
        type_=PREVIOUS_USER_ROLE,
        existing_nullable=False,
    )