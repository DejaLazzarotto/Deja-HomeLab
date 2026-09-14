"""Adiciona o Deja Fotos ao catálogo de módulos.

Revision ID: 20260914_0019
Revises: 20260912_0018
Create Date: 2026-09-14
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "20260914_0019"
down_revision: str | None = "20260912_0018"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

MODULE_KEY_LENGTH = 64
MODULE_KEY = "fotos"


def upgrade() -> None:
    """Instala o Deja Fotos sem liberá-lo para organizações."""

    modules_table = sa.table(
        "modules",
        sa.column(
            "key",
            sa.String(length=MODULE_KEY_LENGTH),
        ),
        sa.column(
            "name",
            sa.String(length=100),
        ),
        sa.column(
            "description",
            sa.String(length=500),
        ),
        sa.column(
            "display_order",
            sa.Integer(),
        ),
    )

    op.bulk_insert(
        modules_table,
        [
            {
                "key": MODULE_KEY,
                "name": "Fotos",
                "description": (
                    "Gestão de álbuns, mídias, pessoas e curadoria "
                    "com reconhecimento facial."
                ),
                "display_order": 50,
            }
        ],
    )


def downgrade() -> None:
    """Remove liberações e o Deja Fotos do catálogo."""

    connection = op.get_bind()

    connection.execute(
        sa.text(
            "DELETE FROM organization_modules "
            "WHERE module_key = :module_key"
        ),
        {
            "module_key": MODULE_KEY,
        },
    )

    connection.execute(
        sa.text(
            "DELETE FROM modules "
            "WHERE `key` = :module_key"
        ),
        {
            "module_key": MODULE_KEY,
        },
    )