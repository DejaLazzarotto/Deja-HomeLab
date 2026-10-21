"""Cria o catálogo de módulos e as liberações por organização.

Revision ID: 20260824_0012
Revises: 20260823_0011
Create Date: 2026-08-24
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260824_0012"
down_revision: str | None = "20260823_0011"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

MODULE_KEY_LENGTH = 64


def upgrade() -> None:
    """Cria o catálogo e libera os módulos para organizações existentes."""

    op.create_table(
        "modules",
        sa.Column(
            "key",
            sa.String(length=MODULE_KEY_LENGTH),
            nullable=False,
        ),
        sa.Column(
            "name",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "description",
            sa.String(length=500),
            nullable=True,
        ),
        sa.Column(
            "display_order",
            sa.Integer(),
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
        sa.PrimaryKeyConstraint(
            "key",
            name="pk_modules",
        ),
    )

    op.create_table(
        "organization_modules",
        sa.Column(
            "organization_id",
            sa.String(length=36),
            nullable=False,
        ),
        sa.Column(
            "module_key",
            sa.String(length=MODULE_KEY_LENGTH),
            nullable=False,
        ),
        sa.Column(
            "enabled",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("0"),
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
            name="fk_organization_modules_organization_id",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["module_key"],
            ["modules.key"],
            name="fk_organization_modules_module_key",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint(
            "organization_id",
            "module_key",
            name="pk_organization_modules",
        ),
    )

    op.create_index(
        "ix_organization_modules_organization_id",
        "organization_modules",
        ["organization_id"],
        unique=False,
    )

    modules_table = sa.table(
        "modules",
        sa.column("key", sa.String(length=MODULE_KEY_LENGTH)),
        sa.column("name", sa.String(length=100)),
        sa.column("description", sa.String(length=500)),
        sa.column("display_order", sa.Integer()),
    )

    initial_modules = [
        {
            "key": "indicators",
            "name": "Indicadores",
            "description": (
                "Gestão de indicadores e visão geral no dashboard."
            ),
            "display_order": 10,
        },
        {
            "key": "measurements",
            "name": "Coleta Manual",
            "description": (
                "Lançamento e gerenciamento manual de medições."
            ),
            "display_order": 20,
        },
        {
            "key": "reports",
            "name": "Relatórios Gerenciais",
            "description": (
                "Consulta e emissão de relatórios gerenciais."
            ),
            "display_order": 30,
        },
    ]

    op.bulk_insert(
        modules_table,
        initial_modules,
    )

    connection = op.get_bind()
    organization_ids = connection.execute(
        sa.text("SELECT id FROM organizations ORDER BY id")
    ).scalars()

    existing_organization_modules = [
        {
            "organization_id": organization_id,
            "module_key": module["key"],
            "enabled": True,
        }
        for organization_id in organization_ids
        for module in initial_modules
    ]

    if existing_organization_modules:
        organization_modules_table = sa.table(
            "organization_modules",
            sa.column("organization_id", sa.String(length=36)),
            sa.column(
                "module_key",
                sa.String(length=MODULE_KEY_LENGTH),
            ),
            sa.column("enabled", sa.Boolean()),
        )
        op.bulk_insert(
            organization_modules_table,
            existing_organization_modules,
        )


def downgrade() -> None:
    """Remove as liberações organizacionais e o catálogo de módulos."""

    op.drop_index(
        "ix_organization_modules_organization_id",
        table_name="organization_modules",
    )
    op.drop_table("organization_modules")
    op.drop_table("modules")