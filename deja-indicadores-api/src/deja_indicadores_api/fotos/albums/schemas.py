from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class FotosAlbumBase(BaseModel):
    """Campos aceitos na criação e atualização de álbuns."""

    environment_id: str = Field(
        min_length=36,
        max_length=36,
    )

    name: str = Field(
        min_length=1,
        max_length=150,
    )

    description: str | None = Field(
        default=None,
        max_length=5000,
    )

    active: bool = True

    @field_validator("name", mode="before")
    @classmethod
    def normalize_name(
        cls,
        value: str,
    ) -> str:
        """Remove espaços excedentes do nome do álbum."""

        return value.strip()

    @field_validator("description", mode="before")
    @classmethod
    def normalize_description(
        cls,
        value: str | None,
    ) -> str | None:
        """Normaliza a descrição opcional."""

        if value is None:
            return None

        normalized = value.strip()

        return normalized or None


class FotosAlbumCreate(FotosAlbumBase):
    """Dados aceitos no cadastro de um álbum."""


class FotosAlbumUpdate(FotosAlbumBase):
    """Dados aceitos na atualização integral de um álbum."""


class FotosAlbumResponse(FotosAlbumBase):
    """Representação pública de um álbum do Deja Fotos."""

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: str

    organization_id: str
    tenant_id: str

    created_at: datetime
    updated_at: datetime