"""Endpoints publicos de verificacao de conta do Fotos PWA."""

from fastapi import APIRouter, HTTPException, Request, status

from deja_indicadores_api.fotos.authentication.confirmation import (
    FotosVerificationInvalidCodeError,
    FotosVerificationInvalidPasswordError,
)
from deja_indicadores_api.fotos.authentication.dependencies import (
    FotosVerificationConfirmationDependency,
    FotosVerificationRequestDependency,
)
from deja_indicadores_api.fotos.authentication.models import (
    FotosVerificationPurpose,
)
from deja_indicadores_api.fotos.authentication.schemas import (
    FotosVerificationConfirmationResponseSchema,
    FotosVerificationConfirmationSchema,
    FotosVerificationRequestResponseSchema,
    FotosVerificationRequestSchema,
)

router = APIRouter(
    prefix="/fotos/auth",
    tags=["Fotos - Autenticacao"],
)


def request_verification_code(
    *,
    request: Request,
    payload: FotosVerificationRequestSchema,
    service: FotosVerificationRequestDependency,
    purpose: FotosVerificationPurpose,
) -> FotosVerificationRequestResponseSchema:
    """Processa solicitacoes sem revelar a existencia da conta."""

    if request.client is None:
        raise RuntimeError("Nao foi possivel identificar a origem da requisicao.")

    service.request_code(
        organization_code=payload.organization_code,
        email=str(payload.email),
        purpose=purpose,
        client_ip=request.client.host,
    )

    return FotosVerificationRequestResponseSchema()


@router.post(
    "/activation/request",
    response_model=FotosVerificationRequestResponseSchema,
    status_code=status.HTTP_202_ACCEPTED,
)
def request_activation(
    request: Request,
    payload: FotosVerificationRequestSchema,
    service: FotosVerificationRequestDependency,
) -> FotosVerificationRequestResponseSchema:
    """Solicita um codigo para ativar a conta Fotos."""

    return request_verification_code(
        request=request,
        payload=payload,
        service=service,
        purpose=FotosVerificationPurpose.ACTIVATION,
    )


@router.post(
    "/password-reset/request",
    response_model=FotosVerificationRequestResponseSchema,
    status_code=status.HTTP_202_ACCEPTED,
)
def request_password_reset(
    request: Request,
    payload: FotosVerificationRequestSchema,
    service: FotosVerificationRequestDependency,
) -> FotosVerificationRequestResponseSchema:
    """Solicita um codigo para recuperar a senha Fotos."""

    return request_verification_code(
        request=request,
        payload=payload,
        service=service,
        purpose=FotosVerificationPurpose.PASSWORD_RESET,
    )


def confirm_verification_code(
    *,
    request: Request,
    payload: FotosVerificationConfirmationSchema,
    service: FotosVerificationConfirmationDependency,
    purpose: FotosVerificationPurpose,
) -> FotosVerificationConfirmationResponseSchema:
    """Confirma o codigo sem revelar detalhes sobre a conta."""

    if request.client is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nao foi possivel processar a confirmacao.",
        )

    try:
        service.confirm(
            organization_code=payload.organization_code,
            email=str(payload.email),
            purpose=purpose,
            code=payload.code,
            new_password=payload.new_password,
            client_ip=request.client.host,
        )
    except (
        FotosVerificationInvalidCodeError,
        FotosVerificationInvalidPasswordError,
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Codigo invalido ou expirado. Solicite um novo codigo.",
        ) from None

    return FotosVerificationConfirmationResponseSchema()


@router.post(
    "/activation/confirm",
    response_model=FotosVerificationConfirmationResponseSchema,
    status_code=status.HTTP_200_OK,
)
def confirm_activation(
    request: Request,
    payload: FotosVerificationConfirmationSchema,
    service: FotosVerificationConfirmationDependency,
) -> FotosVerificationConfirmationResponseSchema:
    """Ativa a conta Fotos e define sua primeira senha."""

    return confirm_verification_code(
        request=request,
        payload=payload,
        service=service,
        purpose=FotosVerificationPurpose.ACTIVATION,
    )


@router.post(
    "/password-reset/confirm",
    response_model=FotosVerificationConfirmationResponseSchema,
    status_code=status.HTTP_200_OK,
)
def confirm_password_reset(
    request: Request,
    payload: FotosVerificationConfirmationSchema,
    service: FotosVerificationConfirmationDependency,
) -> FotosVerificationConfirmationResponseSchema:
    """Confirma a recuperacao de acesso e define uma nova senha."""

    return confirm_verification_code(
        request=request,
        payload=payload,
        service=service,
        purpose=FotosVerificationPurpose.PASSWORD_RESET,
    )
