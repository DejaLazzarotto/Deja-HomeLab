"""Integracao HTTP da autenticacao publica do Fotos PWA."""

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from deja_indicadores_api.core.config import get_settings
from deja_indicadores_api.core.database import get_db_session
from deja_indicadores_api.fotos.authentication.dependencies import (
    get_fotos_verification_request_service,
)
from deja_indicadores_api.fotos.authentication.rate_limit_models import (
    FotosAuthRateLimitModel,
)
from deja_indicadores_api.main import app


def test_http_request_uses_persistent_rate_limits(
    test_session_factory: sessionmaker[Session],
) -> None:
    """Aplica limite real antes de consultar uma conta inexistente."""

    def override_session():
        with test_session_factory() as session:
            yield session

    def override_service():
        from deja_indicadores_api.core.email import EmailService
        from deja_indicadores_api.fotos.authentication.rate_limit_service import (
            FotosAuthRateLimitService,
        )
        from deja_indicadores_api.fotos.authentication.request import (
            FotosVerificationRequestService,
        )
        from deja_indicadores_api.fotos.authentication.service import (
            FotosVerificationCodeService,
        )

        settings = get_settings()

        with test_session_factory() as session:
            yield FotosVerificationRequestService(
                session=session,
                code_service=FotosVerificationCodeService(settings.fotos_verification_secret_key),
                email_service=EmailService(settings),
                rate_limit_service=FotosAuthRateLimitService(
                    session_factory=test_session_factory,
                    secret_key=settings.fotos_verification_secret_key,
                ),
            )

    app.dependency_overrides[get_db_session] = override_session
    app.dependency_overrides[get_fotos_verification_request_service] = override_service

    try:
        with TestClient(app) as client:
            responses = [
                client.post(
                    "/api/fotos/auth/password-reset/request",
                    json={
                        "organization_code": "organizacao-inexistente",
                        "email": "inexistente@example.com",
                    },
                )
                for _ in range(5)
            ]

        assert all(response.status_code == 202 for response in responses)

        messages = [response.json() for response in responses]
        assert all(message == messages[0] for message in messages)

        with test_session_factory() as session:
            records = session.scalars(select(FotosAuthRateLimitModel)).all()

            assert len(records) == 2

            counts = {record.scope: record.request_count for record in records}

            assert counts["ip"] == 5
            assert counts["account"] == 4

    finally:
        app.dependency_overrides.pop(get_db_session, None)
        app.dependency_overrides.pop(
            get_fotos_verification_request_service,
            None,
        )
