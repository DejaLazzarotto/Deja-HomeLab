from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from deja_indicadores_api.core.exceptions import ApplicationError


def application_error_handler(
    request: Request,
    exception: ApplicationError,
) -> JSONResponse:
    """Converte erros controlados da aplicação em respostas HTTP."""

    return JSONResponse(
        status_code=exception.status_code,
        content={
            "error": exception.error_code,
            "message": exception.message,
        },
        headers=exception.headers,
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Registra os manipuladores globais de exceções."""

    app.add_exception_handler(ApplicationError, application_error_handler)
