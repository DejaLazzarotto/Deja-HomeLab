"""Amplia os escopos de limitacao da autenticacao Fotos.

Revision ID: 20261009_0035
Revises: 20261009_0034
Create Date: 2026-10-09
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20261009_0035"
down_revision: str | None = "20261009_0034"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Permite contadores independentes para confirmacao de codigos."""

    op.drop_constraint(
        "ck_fotos_auth_rate_limits_scope",
        "fotos_auth_rate_limits",
        type_="check",
    )

    op.create_check_constraint(
        "ck_fotos_auth_rate_limits_scope",
        "fotos_auth_rate_limits",
        "scope IN ('ip', 'account', 'confirm_ip', 'confirm_account')",
    )


def downgrade() -> None:
    """Restaura os escopos originais, quando nao houver dados novos."""

    connection = op.get_bind()

    count = connection.scalar(
        sa.text(
            "SELECT COUNT(*) FROM fotos_auth_rate_limits "
            "WHERE scope IN ('confirm_ip', 'confirm_account')"
        )
    )

    if count:
        raise RuntimeError(
            "Nao e possivel reverter a migracao com contadores de confirmacao existentes."
        )

    op.drop_constraint(
        "ck_fotos_auth_rate_limits_scope",
        "fotos_auth_rate_limits",
        type_="check",
    )

    op.create_check_constraint(
        "ck_fotos_auth_rate_limits_scope",
        "fotos_auth_rate_limits",
        "scope IN ('ip', 'account')",
    )
