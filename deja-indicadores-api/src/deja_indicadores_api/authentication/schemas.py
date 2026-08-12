from pydantic import BaseModel, EmailStr, Field, field_validator


class LoginRequest(BaseModel):
    """Credenciais necessárias para iniciar uma sessão."""

    organization_id: str = Field(
        min_length=36,
        max_length=36,
    )
    email: EmailStr
    password: str = Field(
        min_length=8,
        max_length=128,
    )

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value: object) -> object:
        """Normaliza o e-mail antes da validação."""

        if isinstance(value, str):
            return value.strip().lower()

        return value


class AccessTokenResponse(BaseModel):
    """Token JWT emitido após autenticação bem-sucedida."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int