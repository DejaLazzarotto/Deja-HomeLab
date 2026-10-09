"""Adiciona controle de entrega aos codigos de verificacao do Fotos.

Revision ID: 20261009_0033
Revises: 20261009_0032
Create Date: 2026-10-09
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20261009_0033"
down_revision: str | None = "20261009_0032"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Adiciona o estado de entrega de cada codigo."""

    op.add_column(
        "fotos_verification_codes",
        sa.Column(
            "delivery_status",
            sa.String(16),
            nullable=False,
            server_default="pending",
        ),
    )

    op.create_check_constraint(
        "ck_fotos_verification_codes_delivery_status",
        "fotos_verification_codes",
        "delivery_status IN ('pending', 'sent', 'failed')",
    )


def downgrade() -> None:
    """Remove o controle de entrega dos codigos."""

    op.drop_constraint(
        "ck_fotos_verification_codes_delivery_status",
        "fotos_verification_codes",
        type_="check",
    )

    op.drop_column(
        "fotos_verification_codes",
        "delivery_status",
    )
