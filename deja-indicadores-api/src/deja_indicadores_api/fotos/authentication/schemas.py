"""Schemas publicos de ativacao e recuperacao de senha do Fotos PWA."""

from pydantic import BaseModel, EmailStr, Field, field_validator


class FotosVerificationRequestSchema(BaseModel):
    """Identifica a conta sem exigir autenticacao previa."""

    organization_code: str = Field(
        min_length=1,
        max_length=100,
    )
    email: EmailStr

    @field_validator("organization_code")
    @classmethod
    def normalize_organization_code(cls, value: str) -> str:
        """Normaliza o codigo da organizacao."""

        normalized = value.strip()

        if not normalized:
            raise ValueError("O codigo da organizacao e obrigatorio.")

        return normalized


class FotosVerificationRequestResponseSchema(BaseModel):
    """Resposta generica que nao revela a existencia da conta."""

    message: str = (
        "Se os dados informados estiverem cadastrados e habilitados, "
        "voce recebera um codigo de verificacao por e-mail."
    )


class FotosVerificationConfirmationSchema(FotosVerificationRequestSchema):
    """Dados para confirmar um codigo e definir uma senha."""

    code: str = Field(
        min_length=6,
        max_length=6,
        pattern=r"^[0-9]{6}$",
    )

    new_password: str = Field(
        min_length=8,
        max_length=128,
    )


class FotosVerificationConfirmationResponseSchema(BaseModel):
    """Resposta publica apos confirmacao bem-sucedida."""

    message: str = "Senha definida com sucesso."
