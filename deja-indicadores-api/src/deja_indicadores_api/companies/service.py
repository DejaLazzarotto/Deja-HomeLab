from uuid import uuid4

from deja_indicadores_api.companies.exceptions import (
    CompanyDocumentAlreadyExistsError,
    CompanyNotFoundError,
)
from deja_indicadores_api.companies.models import CompanyModel
from deja_indicadores_api.companies.repository import CompanyRepository
from deja_indicadores_api.companies.schemas import CompanyCreate, CompanyUpdate


class CompanyService:
    """Regras de aplicação da Gestão de Empresas."""

    def __init__(self, repository: CompanyRepository) -> None:
        self._repository = repository

    def list(self) -> list[CompanyModel]:
        """Lista todas as empresas cadastradas."""

        return self._repository.list()

    def find_by_id(self, company_id: str) -> CompanyModel:
        """Retorna uma empresa pelo identificador."""

        company = self._repository.find_by_id(company_id)

        if company is None:
            raise CompanyNotFoundError(company_id)

        return company

    def create(self, input_data: CompanyCreate) -> CompanyModel:
        """Cadastra uma nova empresa."""

        existing_company = self._repository.find_by_document(input_data.document)

        if existing_company is not None:
            raise CompanyDocumentAlreadyExistsError(input_data.document)

        company = CompanyModel(
            id=str(uuid4()),
            **input_data.model_dump(),
        )

        return self._repository.add(company)

    def update(
        self,
        company_id: str,
        input_data: CompanyUpdate,
    ) -> CompanyModel:
        """Atualiza integralmente uma empresa existente."""

        company = self.find_by_id(company_id)
        document_owner = self._repository.find_by_document(input_data.document)

        if document_owner is not None and document_owner.id != company_id:
            raise CompanyDocumentAlreadyExistsError(input_data.document)

        for field_name, value in input_data.model_dump().items():
            setattr(company, field_name, value)

        return self._repository.update(company)

    def delete(self, company_id: str) -> None:
        """Exclui uma empresa existente."""

        company = self.find_by_id(company_id)
        self._repository.delete(company)
