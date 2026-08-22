"""Adiciona código amigável às organizações.

Revision ID: 20260821_0010
Revises: 20260815_0009
Create Date: 2026-08-21
"""

import re
import unicodedata
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260821_0010"
down_revision: str | None = "20260815_0009"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

MAX_CODE_LENGTH = 32


def _normalize_code(name: str) -> str:
    """Gera um código inicial legível a partir do nome."""

    normalized_name = unicodedata.normalize("NFKD", name)
    ascii_name = normalized_name.encode("ascii", "ignore").decode("ascii")
    code = re.sub(r"[^A-Z0-9]+", "-", ascii_name.upper()).strip("-")
    return code[:MAX_CODE_LENGTH].rstrip("-") or "ORG"


def _unique_code(base_code: str, used_codes: set[str]) -> str:
    """Evita colisões entre códigos gerados pela migração."""

    candidate = base_code
    sequence = 2

    while candidate in used_codes:
        suffix = f"-{sequence}"
        available_length = MAX_CODE_LENGTH - len(suffix)
        candidate = f"{base_code[:available_length].rstrip('-')}{suffix}"
        sequence += 1

    used_codes.add(candidate)
    return candidate


def upgrade() -> None:
    """Adiciona e preenche o código público das organizações."""

    with op.batch_alter_table("organizations") as batch_op:
        batch_op.add_column(
            sa.Column(
                "code",
                sa.String(length=MAX_CODE_LENGTH),
                nullable=True,
            )
        )

    connection = op.get_bind()
    organizations = connection.execute(
        sa.text("SELECT id, name FROM organizations ORDER BY id")
    ).mappings()
    used_codes: set[str] = set()

    for organization in organizations:
        code = _unique_code(
            _normalize_code(organization["name"]),
            used_codes,
        )
        connection.execute(
            sa.text("UPDATE organizations SET code = :code WHERE id = :organization_id"),
            {
                "code": code,
                "organization_id": organization["id"],
            },
        )

    with op.batch_alter_table("organizations") as batch_op:
        batch_op.alter_column(
            "code",
            existing_type=sa.String(length=MAX_CODE_LENGTH),
            nullable=False,
        )
        batch_op.create_unique_constraint(
            "uq_organizations_code",
            ["code"],
        )


def downgrade() -> None:
    """Remove o código público das organizações."""

    with op.batch_alter_table("organizations") as batch_op:
        batch_op.drop_constraint(
            "uq_organizations_code",
            type_="unique",
        )
        batch_op.drop_column("code")
