"""create fotos face processing jobs

Revision ID: 1851c06620e7
Revises: bc574d2037ad
Create Date: 2026-10-26 15:20:15.574880
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "1851c06620e7"
down_revision: str | None = "bc574d2037ad"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Cria a fila persistente de processamento facial."""

    op.create_table(
        "fotos_face_jobs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "media_id",
            sa.String(36),
            sa.ForeignKey("fotos_media.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("organization_id", sa.String(36), nullable=False),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("environment_id", sa.String(36), nullable=False),
        sa.Column(
            "status",
            sa.String(20),
            nullable=False,
            server_default="pending",
        ),
        sa.Column(
            "attempts",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "max_attempts",
            sa.Integer(),
            nullable=False,
            server_default="3",
        ),
        sa.Column("last_error", sa.String(2000), nullable=True),
        sa.Column("claim_token", sa.String(36), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("next_attempt_at", sa.DateTime(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.UniqueConstraint(
            "media_id",
            name="uq_fotos_face_jobs_media",
        ),
        sa.CheckConstraint(
            "status IN ('pending', 'processing', 'completed', 'failed')",
            name="ck_fotos_face_jobs_status",
        ),
        sa.CheckConstraint(
            "attempts >= 0 AND max_attempts > 0",
            name="ck_fotos_face_jobs_attempts",
        ),
        mysql_engine="InnoDB",
    )

    op.create_index(
        "ix_fotos_face_jobs_status_schedule",
        "fotos_face_jobs",
        ["status", "next_attempt_at", "created_at"],
    )

    op.create_index(
        "ix_fotos_face_jobs_environment_status",
        "fotos_face_jobs",
        ["environment_id", "status"],
    )


def downgrade() -> None:
    """Remove a fila de processamento facial."""

    op.drop_index(
        "ix_fotos_face_jobs_environment_status",
        table_name="fotos_face_jobs",
    )

    op.drop_index(
        "ix_fotos_face_jobs_status_schedule",
        table_name="fotos_face_jobs",
    )

    op.drop_table("fotos_face_jobs")
