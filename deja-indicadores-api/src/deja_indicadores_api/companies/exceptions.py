from deja_indicadores_api.core.exceptions import (
    ResourceConflictError,
    ResourceNotFoundError,
)


class CompanyNotFoundError(ResourceNotFoundError):
    """Empresa solicitada não encontrada."""

    error_code = "company_not_found"

    def __init__(self, company_id: str) -> None:
        super().__init__(f"Empresa com ID '{company_id}' não encontrada.")


class CompanyDocumentAlreadyExistsError(ResourceConflictError):
    """Documento já vinculado a outra empresa."""

    error_code = "company_document_already_exists"

    def __init__(self, document: str) -> None:
        super().__init__(f"Já existe uma empresa cadastrada com o documento '{document}'.")
