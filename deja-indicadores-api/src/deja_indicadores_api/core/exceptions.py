from collections.abc import Mapping


class ApplicationError(Exception):
    """Erro-base controlado pela aplicação."""

    status_code = 400
    error_code = "application_error"

    def __init__(
        self,
        message: str,
        headers: Mapping[str, str] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.headers = dict(headers) if headers is not None else None


class ResourceNotFoundError(ApplicationError):
    """Recurso solicitado não encontrado."""

    status_code = 404
    error_code = "resource_not_found"


class ResourceConflictError(ApplicationError):
    """Conflito entre o recurso informado e o estado atual."""

    status_code = 409
    error_code = "resource_conflict"
