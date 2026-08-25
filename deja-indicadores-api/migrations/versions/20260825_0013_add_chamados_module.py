"""Adiciona o Deja Chamados ao catálogo de módulos.

Revision ID: 20260825_0013
Revises: 20260824_0012
Create Date: 2026-08-25
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260825_0013"
down_revision: str | None = "20260824_0012"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

MODULE_KEY_LENGTH = 64
MODULE_KEY = "chamados"


def upgrade() -> None:
    """Instala o Deja Chamados sem liberá-lo para organizações."""

    modules_table = sa.table(
        "modules",
        sa.column("key", sa.String(length=MODULE_KEY_LENGTH)),
        sa.column("name", sa.String(length=100)),
        sa.column("description", sa.String(length=500)),
        sa.column("display_order", sa.Integer()),
    )

    op.bulk_insert(
        modules_table,
        [
            {
                "key": MODULE_KEY,
                "name": "Chamados",
                "description": ("Gestão de clientes, chamados e atendimento técnico."),
                "display_order": 40,
            }
        ],
    )


def downgrade() -> None:
    """Remove as liberações e o Deja Chamados do catálogo."""

    connection = op.get_bind()
    connection.execute(
        sa.text("DELETE FROM organization_modules WHERE module_key = :module_key"),
        {"module_key": MODULE_KEY},
    )
    connection.execute(
        sa.text("DELETE FROM modules WHERE `key` = :module_key"),
        {"module_key": MODULE_KEY},
    )
