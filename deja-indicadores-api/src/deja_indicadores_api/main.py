from fastapi import FastAPI

from deja_indicadores_api.api.router import api_router
from deja_indicadores_api.core.config import get_settings
from deja_indicadores_api.core.exception_handlers import register_exception_handlers


def create_app() -> FastAPI:
    """Cria e configura a aplicação FastAPI."""

    settings = get_settings()
    expose_api_documentation = settings.app_env != "production"

    app = FastAPI(
        title=settings.app_name,
        debug=settings.app_debug,
        version="0.1.0",
        docs_url="/docs" if expose_api_documentation else None,
        redoc_url="/redoc" if expose_api_documentation else None,
        openapi_url="/openapi.json" if expose_api_documentation else None,
    )

    register_exception_handlers(app)
    app.include_router(api_router, prefix="/api")

    @app.get("/health", tags=["Health"])
    def health_check() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
