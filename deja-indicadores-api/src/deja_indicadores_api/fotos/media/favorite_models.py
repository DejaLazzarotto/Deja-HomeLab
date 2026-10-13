"""Modelo de favoritos individuais de mídias do Deja Fotos."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from deja_indicadores_api.core.database import Base


class FotosMediaFavoriteModel(Base):
    """Vínculo entre um usuário e uma mídia favorita."""

    __tablename__ = "fotos_media_favorites"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "media_id",
            name="uq_fotos_media_favorites_user_media",
        ),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
    )

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "users.id",
            name="fk_fotos_media_favorites_user_id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    media_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "fotos_media.id",
            name="fk_fotos_media_favorites_media_id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )