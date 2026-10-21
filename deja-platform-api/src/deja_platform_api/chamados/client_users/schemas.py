from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ChamadosClientUserCreate(BaseModel):
    """Dados aceitos para vincular um usuário a um Cliente."""

    user_id: str = Field(
        min_length=36,
        max_length=36,
    )

    client_id: str = Field(
        min_length=36,
        max_length=36,
    )


class ChamadosClientUserUpdate(BaseModel):
    """Dados aceitos para alterar o Cliente vinculado."""

    client_id: str = Field(
        min_length=36,
        max_length=36,
    )


class ChamadosClientUserResponse(BaseModel):
    """Representação pública do vínculo de usuário com Cliente."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    client_id: str
    created_at: datetime