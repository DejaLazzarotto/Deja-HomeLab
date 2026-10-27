"""add fotos media curation completion

Revision ID: 08453cc623c8
Revises: 1851c06620e7
Create Date: 2026-10-27 00:21:19.971398
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa



revision: str = '08453cc623c8'
down_revision: str | None = '1851c06620e7'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Aplica as alterações desta migration."""

    op.add_column("fotos_media", sa.Column("curation_completed", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("fotos_media", sa.Column("curation_completed_at", sa.DateTime(), nullable=True))
    op.alter_column("fotos_media", "curation_completed", existing_type=sa.Boolean(), existing_nullable=False, server_default=None)



def downgrade() -> None:
    """Reverte as alterações desta migration."""

    op.drop_column("fotos_media", "curation_completed_at")
    op.drop_column("fotos_media", "curation_completed")
