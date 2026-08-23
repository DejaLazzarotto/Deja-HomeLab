from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
)


class ChamadosClientBase(BaseModel):
    """Campos aceitos na criação e atualização de clientes."""

    environment_id: str = Field(
        min_length=36,
        max_length=36,
    )

    company_name: str = Field(
        min_length=1,
        max_length=255,
    )
    fantasy_name: str = Field(
        min_length=1,
        max_length=255,
    )
    document: str = Field(
        min_length=11,
        max_length=14,
    )

    contact_name: str = Field(
        min_length=1,
        max_length=255,
    )

    phone: str = Field(
        min_length=10,
        max_length=11,
    )
    whatsapp: str = Field(
        min_length=10,
        max_length=11,
    )
    email: EmailStr

    city: str = Field(
        min_length=1,
        max_length=100,
    )
    state: str = Field(
        min_length=2,
        max_length=2,
    )

    notes: str = Field(
        default="",
        max_length=1000,
    )

    active: bool = True

    @field_validator(
        "company_name",
        "fantasy_name",
        "contact_name",
        "city",
        mode="before",
    )
    @classmethod
    def normalize_required_text(
        cls,
        value: str,
    ) -> str:
        """Remove espaços excedentes dos textos obrigatórios."""

        return value.strip()

    @field_validator("document", mode="before")
    @classmethod
    def normalize_document(
        cls,
        value: str,
    ) -> str:
        """Mantém somente os números do CPF ou CNPJ."""

        normalized = "".join(character for character in value if character.isdigit())

        if len(normalized) not in (11, 14):
            raise ValueError("O documento deve possuir 11 ou 14 números.")

        return normalized

    @field_validator(
        "phone",
        "whatsapp",
        mode="before",
    )
    @classmethod
    def normalize_phone(
        cls,
        value: str,
    ) -> str:
        """Mantém somente os dez ou onze números do telefone."""

        normalized = "".join(character for character in value if character.isdigit())

        if len(normalized) not in (10, 11):
            raise ValueError("O telefone deve possuir 10 ou 11 números.")

        return normalized

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(
        cls,
        value: str,
    ) -> str:
        """Normaliza o endereço de e-mail."""

        return value.strip().lower()

    @field_validator("state", mode="before")
    @classmethod
    def normalize_state(
        cls,
        value: str,
    ) -> str:
        """Normaliza a sigla da unidade federativa."""

        normalized = value.strip().upper()

        if len(normalized) != 2:
            raise ValueError("O estado deve possuir duas letras.")

        return normalized

    @field_validator("notes", mode="before")
    @classmethod
    def normalize_notes(
        cls,
        value: str,
    ) -> str:
        """Remove espaços excedentes das observações."""

        return value.strip()


class ChamadosClientCreate(ChamadosClientBase):
    """Dados aceitos no cadastro de um cliente."""


class ChamadosClientUpdate(ChamadosClientBase):
    """Dados aceitos na atualização integral de um cliente."""


class ChamadosClientResponse(ChamadosClientBase):
    """Representação pública de um cliente do Deja Chamados."""

    model_config = ConfigDict(from_attributes=True)

    id: str

    organization_id: str
    tenant_id: str

    created_at: datetime
    updated_at: datetime

    total_tickets: int = 0
