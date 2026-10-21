"""Rostos e referências faciais separadas dos avatares.

Revision ID: 20260924_0028
Revises: 20260923_0027
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260924_0028"
down_revision: str | None = "20260923_0027"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "fotos_faces",
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
        sa.Column("x", sa.Float(), nullable=False),
        sa.Column("y", sa.Float(), nullable=False),
        sa.Column("width", sa.Float(), nullable=False),
        sa.Column("height", sa.Float(), nullable=False),
        sa.Column("origin", sa.String(20), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column(
            "person_id", sa.String(36), sa.ForeignKey("fotos_people.id", ondelete="SET NULL")
        ),
        sa.Column(
            "rejected_person_id",
            sa.String(36),
            sa.ForeignKey("fotos_people.id", ondelete="SET NULL"),
        ),
        sa.Column("confidence", sa.Float()),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_fotos_faces_scope_status", "fotos_faces", ["environment_id", "status"])
    op.create_index("ix_fotos_faces_media_status", "fotos_faces", ["media_id", "status"])
    op.create_table(
        "fotos_face_references",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "face_id",
            sa.String(36),
            sa.ForeignKey("fotos_faces.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "person_id",
            sa.String(36),
            sa.ForeignKey("fotos_people.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("organization_id", sa.String(36), nullable=False),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("environment_id", sa.String(36), nullable=False),
        sa.Column("storage_key", sa.String(512), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("face_id", name="uq_fotos_face_reference_face"),
    )
    op.create_index(
        "ix_fotos_face_references_environment_id", "fotos_face_references", ["environment_id"]
    )


def downgrade() -> None:
    op.drop_index("ix_fotos_face_references_environment_id", table_name="fotos_face_references")
    op.drop_table("fotos_face_references")
    op.drop_index("ix_fotos_faces_media_status", table_name="fotos_faces")
    op.drop_index("ix_fotos_faces_scope_status", table_name="fotos_faces")
    op.drop_table("fotos_faces")
