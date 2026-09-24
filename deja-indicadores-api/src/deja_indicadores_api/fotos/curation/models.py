"""Marcações de rostos e referências de reconhecimento."""

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Index, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from deja_indicadores_api.core.database import Base


class FotosFaceModel(Base):
    __tablename__ = "fotos_faces"
    __table_args__ = (
        Index("ix_fotos_faces_scope_status", "environment_id", "status"),
        Index("ix_fotos_faces_media_status", "media_id", "status"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    media_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("fotos_media.id", ondelete="CASCADE"), nullable=False
    )
    organization_id: Mapped[str] = mapped_column(String(36), nullable=False)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False)
    environment_id: Mapped[str] = mapped_column(String(36), nullable=False)
    x: Mapped[float] = mapped_column(Float, nullable=False)
    y: Mapped[float] = mapped_column(Float, nullable=False)
    width: Mapped[float] = mapped_column(Float, nullable=False)
    height: Mapped[float] = mapped_column(Float, nullable=False)
    origin: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    person_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("fotos_people.id", ondelete="SET NULL"), nullable=True
    )
    rejected_person_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("fotos_people.id", ondelete="SET NULL"), nullable=True
    )
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )


class FotosFaceReferenceModel(Base):
    __tablename__ = "fotos_face_references"
    __table_args__ = (UniqueConstraint("face_id", name="uq_fotos_face_reference_face"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    face_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("fotos_faces.id", ondelete="CASCADE"), nullable=False
    )
    person_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("fotos_people.id", ondelete="CASCADE"), nullable=False
    )
    organization_id: Mapped[str] = mapped_column(String(36), nullable=False)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False)
    environment_id: Mapped[str] = mapped_column(String(36), nullable=False)
    storage_key: Mapped[str] = mapped_column(String(512), nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
