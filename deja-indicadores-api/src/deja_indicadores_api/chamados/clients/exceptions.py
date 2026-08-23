from deja_indicadores_api.core.exceptions import (
    ResourceConflictError,
    ResourceNotFoundError,
)


class ChamadosClientNotFoundError(ResourceNotFoundError):
    """Cliente do Deja Chamados não encontrado."""

    error_code = "chamados_client_not_found"

    def __init__(
        self,
        client_id: str,
    ) -> None:
        super().__init__(f"Cliente com ID '{client_id}' não encontrado.")


class ChamadosClientDocumentAlreadyExistsError(ResourceConflictError):
    """Documento já vinculado a outro cliente da organização."""

    error_code = "chamados_client_document_already_exists"

    def __init__(
        self,
        document: str,
    ) -> None:
        super().__init__(
            f"Já existe um cliente cadastrado nesta organização com o documento '{document}'."
        )
