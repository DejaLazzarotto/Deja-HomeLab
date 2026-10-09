"""Testes das dependencias de autenticacao do Fotos PWA."""

from unittest.mock import Mock, patch

from deja_indicadores_api.fotos.authentication.confirmation_request import (
    FotosVerificationConfirmationRequestService,
)
from deja_indicadores_api.fotos.authentication.dependencies import (
    get_fotos_verification_request_service,
)
from deja_indicadores_api.fotos.authentication.request import (
    FotosVerificationRequestService,
)


def test_request_dependency_enables_rate_limiting() -> None:
    """A dependencia publica sempre fornece o controle de requisicoes."""

    session = Mock()
    settings = Mock()
    settings.fotos_verification_secret_key = "a" * 64

    with (
        patch(
            "deja_indicadores_api.fotos.authentication.dependencies.FotosAuthRateLimitService"
        ) as rate_limit_class,
        patch("deja_indicadores_api.fotos.authentication.dependencies.EmailService") as email_class,
        patch(
            "deja_indicadores_api.fotos.authentication.dependencies.SessionLocal"
        ) as session_factory,
    ):
        service = get_fotos_verification_request_service(
            session=session,
            settings=settings,
        )

    assert isinstance(service, FotosVerificationRequestService)
    assert service._rate_limit is rate_limit_class.return_value

    rate_limit_class.assert_called_once_with(
        session_factory=session_factory,
        secret_key=settings.fotos_verification_secret_key,
    )

    email_class.assert_called_once_with(settings)


def test_confirmation_dependency_enables_rate_limiting() -> None:
    """A confirmacao publica recebe obrigatoriamente o rate limiting."""

    from deja_indicadores_api.fotos.authentication.dependencies import (
        get_fotos_verification_confirmation_service,
    )

    session = Mock()
    settings = Mock()
    settings.fotos_verification_secret_key = "a" * 64

    with (
        patch(
            "deja_indicadores_api.fotos.authentication.dependencies.FotosAuthRateLimitService"
        ) as rate_limit_class,
        patch(
            "deja_indicadores_api.fotos.authentication.dependencies.PasswordService"
        ) as password_class,
        patch(
            "deja_indicadores_api.fotos.authentication.dependencies.SessionLocal"
        ) as session_factory,
    ):
        service = get_fotos_verification_confirmation_service(
            session=session,
            settings=settings,
        )

    assert isinstance(
        service,
        FotosVerificationConfirmationRequestService,
    )
    assert service._rate_limit is rate_limit_class.return_value

    rate_limit_class.assert_called_once_with(
        session_factory=session_factory,
        secret_key=settings.fotos_verification_secret_key,
    )

    password_class.assert_called_once_with()
    assert service._confirmation._password_service is password_class.return_value
