from deja_indicadores_api.core.exceptions import (
    ResourceConflictError,
    ResourceNotFoundError,
)


class ChamadosTicketNotFoundError(ResourceNotFoundError):
    """Chamado não encontrado."""

    error_code = "chamados_ticket_not_found"

    def __init__(
        self,
        ticket_id: str,
    ) -> None:
        super().__init__(f"Chamado com ID '{ticket_id}' não encontrado.")


class ChamadosTicketInactiveClientError(ResourceConflictError):
    """Cliente inativo não pode receber novos chamados."""

    error_code = "chamados_ticket_inactive_client"

    def __init__(
        self,
        client_id: str,
    ) -> None:
        super().__init__(
            f"O cliente com ID '{client_id}' está inativo."
        )


class ChamadosTicketAssignedUserNotFoundError(ResourceNotFoundError):
    """Responsável informado não foi encontrado."""

    error_code = "chamados_ticket_assigned_user_not_found"

    def __init__(
        self,
        user_id: str,
    ) -> None:
        super().__init__(
            f"Usuário responsável com ID '{user_id}' não encontrado."
        )


class ChamadosTicketInvalidAssignedUserError(ResourceConflictError):
    """Usuário não pode ser responsável pelo chamado."""

    error_code = "chamados_ticket_invalid_assigned_user"

    def __init__(
        self,
        user_id: str,
    ) -> None:
        super().__init__(
            f"O usuário com ID '{user_id}' não pode ser responsável por este chamado."
        )


class ChamadosTicketInvalidStatusTransitionError(ResourceConflictError):
    """Transição entre estados do chamado não é permitida."""

    error_code = "chamados_ticket_invalid_status_transition"

    def __init__(
        self,
        current_status: str,
        target_status: str,
    ) -> None:
        super().__init__(
            f"Não é permitido alterar o chamado de '{current_status}' para '{target_status}'."
        )