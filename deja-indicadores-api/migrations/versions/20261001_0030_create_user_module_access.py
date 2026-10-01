"""Cria acessos de usuários por módulo da plataforma.

Revision ID: 20261001_0030
Revises: 20260928_0029
Create Date: 2026-10-01
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20261001_0030"
down_revision: str | None = "20260928_0029"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

MODULE_KEY_LENGTH = 64

MODULE_ROLE = sa.Enum(
    "manager",
    "analyst",
    "viewer",
    name="user_module_role",
)


def upgrade() -> None:
    """Cria os acessos por módulo e preserva os acessos atuais."""

    op.create_table(
        "user_module_access",
        sa.Column(
            "user_id",
            sa.String(length=36),
            nullable=False,
        ),
        sa.Column(
            "module_key",
            sa.String(length=MODULE_KEY_LENGTH),
            nullable=False,
        ),
        sa.Column(
            "role",
            MODULE_ROLE,
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
            ["user_id"],
            ["users.id"],
            name="fk_user_module_access_user_id",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["module_key"],
            ["modules.key"],
            name="fk_user_module_access_module_key",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint(
            "user_id",
            "module_key",
            name="pk_user_module_access",
        ),
    )

    op.create_index(
        "ix_user_module_access_module_key",
        "user_module_access",
        ["module_key"],
        unique=False,
    )

    connection = op.get_bind()

    connection.execute(
        sa.text(
            """
            INSERT INTO user_module_access (
                user_id,
                module_key,
                role,
                created_at,
                updated_at
            )
            SELECT
                users.id,
                organization_modules.module_key,
                CASE
                    WHEN users.role = 'analyst'
                        THEN 'analyst'
                    WHEN users.role = 'viewer'
                        THEN 'viewer'
                    ELSE 'manager'
                END,
                CURRENT_TIMESTAMP,
                CURRENT_TIMESTAMP
            FROM users
            INNER JOIN organization_modules
                ON organization_modules.organization_id
                    = users.organization_id
            WHERE
                organization_modules.enabled = 1
                AND users.role IN (
                    'organization_admin',
                    'tenant_admin',
                    'manager',
                    'analyst',
                    'viewer'
                )
            """
        )
    )


def downgrade() -> None:
    """Remove os acessos individuais por módulo."""

    op.drop_index(
        "ix_user_module_access_module_key",
        table_name="user_module_access",
    )

    op.drop_table("user_module_access")