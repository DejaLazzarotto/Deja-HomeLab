from deja_indicadores_api.core.exceptions import (
    ResourceConflictError,
    ResourceNotFoundError,
)


class ChamadosClientUserNotFoundError(ResourceNotFoundError):
    """Vínculo de usuário com Cliente não encontrado."""

    def __init__(
        self,
        user_id: str,
    ) -> None:
        super().__init__(
            f"Não existe Cliente do Chamados vinculado ao usuário '{user_id}'."
        )


class ChamadosClientUserAlreadyExistsError(ResourceConflictError):
    """Usuário já possui vínculo com um Cliente."""

    def __init__(
        self,
        user_id: str,
    ) -> None:
        super().__init__(
            f"O usuário '{user_id}' já possui vínculo com um Cliente do Chamados."
        )