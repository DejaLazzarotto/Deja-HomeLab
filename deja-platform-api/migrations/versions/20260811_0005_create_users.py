"""Cria a tabela de usuários.

Revision ID: 20260811_0005
Revises: 20260810_0004
Create Date: 2026-08-11
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260811_0005"
down_revision: str | None = "20260810_0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Cria usuários e seus vínculos institucionais."""

    user_role = sa.Enum(
        "organization_admin",
        "tenant_admin",
        "manager",
        "analyst",
        "viewer",
        name="user_role",
    )
    user_status = sa.Enum(
        "active",
        "inactive",
        name="user_status",
    )

    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column(
            "organization_id",
            sa.String(length=36),
            nullable=False,
        ),
        sa.Column(
            "tenant_id",
            sa.String(length=36),
            nullable=True,
        ),
        sa.Column(
            "environment_id",
            sa.String(length=36),
            nullable=True,
        ),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column(
            "role",
            user_role,
            nullable=False,
        ),
        sa.Column(
            "status",
            user_status,
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
            name="fk_users_organization_id",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenants.id"],
            name="fk_users_tenant_id",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["environment_id"],
            ["environments.id"],
            name="fk_users_environment_id",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "organization_id",
            "email",
            name="uq_users_organization_email",
        ),
    )

    op.create_index(
        "ix_users_organization_id",
        "users",
        ["organization_id"],
        unique=False,
    )
    op.create_index(
        "ix_users_tenant_id",
        "users",
        ["tenant_id"],
        unique=False,
    )
    op.create_index(
        "ix_users_environment_id",
        "users",
        ["environment_id"],
        unique=False,
    )
    op.create_index(
        "ix_users_email",
        "users",
        ["email"],
        unique=False,
    )


def downgrade() -> None:
    """Remove a tabela de usuários."""

    op.drop_index(
        "ix_users_email",
        table_name="users",
    )
    op.drop_index(
        "ix_users_environment_id",
        table_name="users",
    )
    op.drop_index(
        "ix_users_tenant_id",
        table_name="users",
    )
    op.drop_index(
        "ix_users_organization_id",
        table_name="users",
    )
    op.drop_table("users")