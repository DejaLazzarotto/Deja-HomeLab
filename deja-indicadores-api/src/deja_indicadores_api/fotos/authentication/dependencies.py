"""Dependencias dos endpoints publicos de autenticacao do Fotos PWA."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from deja_indicadores_api.core.config import Settings, get_settings
from deja_indicadores_api.core.database import SessionLocal, get_db_session
from deja_indicadores_api.core.email import EmailService
from deja_indicadores_api.core.security import PasswordService
from deja_indicadores_api.fotos.authentication.confirmation_request import (
    FotosVerificationConfirmationRequestService,
)
from deja_indicadores_api.fotos.authentication.rate_limit_service import (
    FotosAuthRateLimitService,
)
from deja_indicadores_api.fotos.authentication.request import (
    FotosVerificationRequestService,
)
from deja_indicadores_api.fotos.authentication.service import (
    FotosVerificationCodeService,
)


def get_fotos_verification_request_service(
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> FotosVerificationRequestService:
    """Constroi o fluxo de solicitacao com rate limiting obrigatorio."""

    code_service = FotosVerificationCodeService(settings.fotos_verification_secret_key)

    email_service = EmailService(settings)

    rate_limit_service = FotosAuthRateLimitService(
        session_factory=SessionLocal,
        secret_key=settings.fotos_verification_secret_key,
    )

    return FotosVerificationRequestService(
        session=session,
        code_service=code_service,
        email_service=email_service,
        rate_limit_service=rate_limit_service,
    )


FotosVerificationRequestDependency = Annotated[
    FotosVerificationRequestService,
    Depends(get_fotos_verification_request_service),
]


def get_fotos_verification_confirmation_service(
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> FotosVerificationConfirmationRequestService:
    """Constroi a confirmacao com rate limiting obrigatorio."""

    code_service = FotosVerificationCodeService(settings.fotos_verification_secret_key)

    password_service = PasswordService()

    rate_limit_service = FotosAuthRateLimitService(
        session_factory=SessionLocal,
        secret_key=settings.fotos_verification_secret_key,
    )

    return FotosVerificationConfirmationRequestService(
        session=session,
        code_service=code_service,
        password_service=password_service,
        rate_limit_service=rate_limit_service,
    )


FotosVerificationConfirmationDependency = Annotated[
    FotosVerificationConfirmationRequestService,
    Depends(get_fotos_verification_confirmation_service),
]
