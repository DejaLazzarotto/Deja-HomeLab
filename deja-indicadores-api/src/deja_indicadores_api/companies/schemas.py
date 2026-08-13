from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from deja_indicadores_api.companies.models import CompanyStatus


class CompanyBase(BaseModel):
    """Campos compartilhados para criação e atualização de empresas."""

    environment_id: str = Field(min_length=36, max_length=36)
    legal_name: str = Field(min_length=1, max_length=255)
    trade_name: str = Field(min_length=1, max_length=255)
    document: str = Field(min_length=11, max_length=14)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=20)
    status: CompanyStatus = CompanyStatus.ACTIVE

    @field_validator("legal_name", "trade_name", mode="before")
    @classmethod
    def normalize_required_text(cls, value: str) -> str:
        """Remove espaços excedentes dos campos obrigatórios."""

        return value.strip()

    @field_validator("document", mode="before")
    @classmethod
    def normalize_document(cls, value: str) -> str:
        """Mantém somente os números do CPF ou CNPJ."""

        normalized = "".join(character for character in value if character.isdigit())

        if len(normalized) not in (11, 14):
            raise ValueError("O documento deve possuir 11 ou 14 números.")

        return normalized

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value: str | None) -> str | None:
        """Normaliza o endereço de e-mail quando informado."""

        if value is None:
            return None

        normalized = value.strip().lower()
        return normalized or None

    @field_validator("phone", mode="before")
    @classmethod
    def normalize_phone(cls, value: str | None) -> str | None:
        """Remove espaços excedentes do telefone quando informado."""

        if value is None:
            return None

        normalized = value.strip()
        return normalized or None


class CompanyCreate(CompanyBase):
    """Dados aceitos no cadastro de uma empresa."""


class CompanyUpdate(CompanyBase):
    """Dados aceitos na atualização integral de uma empresa."""


class CompanyResponse(CompanyBase):
    """Representação pública de uma empresa retornada pela API."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    updated_at: datetime
