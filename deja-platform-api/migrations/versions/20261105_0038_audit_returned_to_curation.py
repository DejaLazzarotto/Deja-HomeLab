"""Track media returned to curation specifically from audit.

Revision ID: 20261105_0038
Revises: 20261029_0037
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20261105_0038"
down_revision: str | None = "20261029_0037"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "fotos_media",
        sa.Column(
            "audit_returned_to_curation",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )


def downgrade() -> None:
    op.drop_column("fotos_media", "audit_returned_to_curation")
