from deja_indicadores_api.core.exceptions import (
    ApplicationError,
    ResourceNotFoundError,
)


class ChamadosTicketAttachmentNotFoundError(ResourceNotFoundError):
    """Anexo de chamado não encontrado."""

    error_code = "chamados_ticket_attachment_not_found"

    def __init__(
        self,
        attachment_id: str,
    ) -> None:
        super().__init__(
            f"Anexo com ID '{attachment_id}' não encontrado."
        )


class ChamadosTicketAttachmentFileNotFoundError(ResourceNotFoundError):
    """Arquivo físico de um anexo não encontrado."""

    error_code = "chamados_ticket_attachment_file_not_found"

    def __init__(
        self,
        attachment_id: str,
    ) -> None:
        super().__init__(
            f"O arquivo físico do anexo com ID '{attachment_id}' não foi encontrado."
        )


class ChamadosTicketAttachmentInvalidTypeError(ApplicationError):
    """Tipo de arquivo não permitido para anexos."""

    error_code = "chamados_ticket_attachment_invalid_type"

    def __init__(
        self,
        content_type: str,
    ) -> None:
        super().__init__(
            f"O tipo de arquivo '{content_type}' não é permitido para anexos."
        )


class ChamadosTicketAttachmentTooLargeError(ApplicationError):
    """Arquivo excede o tamanho máximo permitido."""

    error_code = "chamados_ticket_attachment_too_large"

    def __init__(
        self,
        max_size_mb: int,
    ) -> None:
        super().__init__(
            f"O anexo excede o tamanho máximo permitido de {max_size_mb} MB."
        )