"""Integracao HTTP da confirmacao publica do Fotos PWA."""

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from deja_indicadores_api.core.config import get_settings
from deja_indicadores_api.core.security import PasswordService
from deja_indicadores_api.fotos.authentication.confirmation_request import (
    FotosVerificationConfirmationRequestService,
)
from deja_indicadores_api.fotos.authentication.dependencies import (
    get_fotos_verification_confirmation_service,
)
from deja_indicadores_api.fotos.authentication.rate_limit_models import (
    FotosAuthRateLimitModel,
)
from deja_indicadores_api.fotos.authentication.rate_limit_service import (
    FotosAuthRateLimitService,
)
from deja_indicadores_api.fotos.authentication.service import (
    FotosVerificationCodeService,
)
from deja_indicadores_api.main import app


def test_http_confirmation_limits_unknown_account(
    test_session_factory: sessionmaker[Session],
) -> None:
    """Limita confirmacoes mesmo quando a conta nao existe."""

    settings = get_settings()

    def override_confirmation_service():
        with test_session_factory() as session:
            yield FotosVerificationConfirmationRequestService(
                session=session,
                code_service=FotosVerificationCodeService(settings.fotos_verification_secret_key),
                password_service=PasswordService(),
                rate_limit_service=FotosAuthRateLimitService(
                    session_factory=test_session_factory,
                    secret_key=settings.fotos_verification_secret_key,
                ),
            )

    app.dependency_overrides[get_fotos_verification_confirmation_service] = (
        override_confirmation_service
    )

    try:
        with TestClient(app) as client:
            responses = [
                client.post(
                    "/api/fotos/auth/activation/confirm",
                    json={
                        "organization_code": "organizacao-inexistente",
                        "email": "inexistente@example.com",
                        "code": "123456",
                        "new_password": "SenhaSegura123",
                    },
                )
                for _ in range(12)
            ]

        assert all(response.status_code == 400 for response in responses)

        messages = [response.json() for response in responses]
        assert all(message == messages[0] for message in messages)

        with test_session_factory() as session:
            records = session.scalars(select(FotosAuthRateLimitModel)).all()

            counts = {record.scope: record.request_count for record in records}

            assert counts == {
                "confirm_ip": 12,
                "confirm_account": 11,
            }

    finally:
        app.dependency_overrides.pop(
            get_fotos_verification_confirmation_service,
            None,
        )


def test_http_activation_sets_password_and_consumes_code(
    client: TestClient,
    test_session_factory: sessionmaker[Session],
    test_app,
) -> None:
    """Define a primeira senha via HTTP e impede reutilizar o codigo."""

    from deja_indicadores_api.core.security import PasswordService
    from deja_indicadores_api.fotos.authentication.issuance import (
        FotosVerificationIssuanceService,
    )
    from deja_indicadores_api.fotos.authentication.models import (
        FotosVerificationCodeModel,
        FotosVerificationPurpose,
    )
    from deja_indicadores_api.user_management.models import UserModel
    from tests.authentication.test_authentication_api import (
        create_organization,
        create_user,
    )

    organization = create_organization(
        client,
        enabled_modules={"fotos"},
    )

    user = create_user(
        client,
        organization_id=str(organization["id"]),
        role="user",
        module_access={"fotos": "viewer"},
    )

    user_id = str(user["id"])
    new_password = "SenhaInicial123"
    code_service = FotosVerificationCodeService("a" * 64)

    with test_session_factory() as session:
        issued = FotosVerificationIssuanceService(
            session,
            code_service,
        ).issue(
            user_id=user_id,
            purpose=FotosVerificationPurpose.ACTIVATION,
        )

    with test_session_factory() as session:
        verification = session.get(
            FotosVerificationCodeModel,
            issued.verification_id,
        )

        assert verification is not None
        verification.delivery_status = "sent"
        session.commit()

    def override_confirmation_service():
        with test_session_factory() as session:
            yield FotosVerificationConfirmationRequestService(
                session=session,
                code_service=code_service,
                password_service=PasswordService(),
                rate_limit_service=FotosAuthRateLimitService(
                    session_factory=test_session_factory,
                    secret_key="a" * 64,
                ),
            )

    test_app.dependency_overrides[get_fotos_verification_confirmation_service] = (
        override_confirmation_service
    )

    payload = {
        "organization_code": str(organization["code"]),
        "email": str(user["email"]),
        "code": issued.code,
        "new_password": new_password,
    }

    try:
        response = client.post(
            "/api/fotos/auth/activation/confirm",
            json=payload,
        )

        assert response.status_code == 200, response.text
        assert response.json() == {"message": "Senha definida com sucesso."}

        with test_session_factory() as session:
            stored_user = session.get(UserModel, user_id)
            stored_code = session.get(
                FotosVerificationCodeModel,
                issued.verification_id,
            )

            assert stored_user is not None
            assert stored_user.password_hash is not None
            assert stored_user.password_hash != new_password
            assert PasswordService().verify(
                new_password,
                stored_user.password_hash,
            )

            assert stored_code is not None
            assert stored_code.consumed_at is not None

        second_response = client.post(
            "/api/fotos/auth/activation/confirm",
            json={
                **payload,
                "new_password": "OutraSenhaInicial123",
            },
        )

        assert second_response.status_code == 400

        with test_session_factory() as session:
            stored_user = session.get(UserModel, user_id)

            assert stored_user is not None
            assert PasswordService().verify(
                new_password,
                stored_user.password_hash,
            )

    finally:
        test_app.dependency_overrides.pop(
            get_fotos_verification_confirmation_service,
            None,
        )


def test_http_password_reset_replaces_password(
    client: TestClient,
    test_session_factory: sessionmaker[Session],
    test_app,
) -> None:
    """Redefine a senha via HTTP e impede reutilizar o codigo."""

    from deja_indicadores_api.fotos.authentication.issuance import (
        FotosVerificationIssuanceService,
    )
    from deja_indicadores_api.fotos.authentication.models import (
        FotosVerificationCodeModel,
        FotosVerificationPurpose,
    )
    from deja_indicadores_api.user_management.models import UserModel
    from tests.authentication.test_authentication_api import (
        create_organization,
        create_user,
    )

    organization = create_organization(
        client,
        enabled_modules={"fotos"},
    )

    user = create_user(
        client,
        organization_id=str(organization["id"]),
        role="user",
        module_access={"fotos": "viewer"},
    )

    user_id = str(user["id"])
    old_password = "SenhaAntiga123"
    new_password = "SenhaNova456"
    password_service = PasswordService()
    code_service = FotosVerificationCodeService("a" * 64)

    with test_session_factory() as session:
        stored_user = session.get(UserModel, user_id)
        assert stored_user is not None

        stored_user.password_hash = password_service.hash(old_password)
        session.commit()

    with test_session_factory() as session:
        issued = FotosVerificationIssuanceService(
            session,
            code_service,
        ).issue(
            user_id=user_id,
            purpose=FotosVerificationPurpose.PASSWORD_RESET,
        )

    with test_session_factory() as session:
        verification = session.get(
            FotosVerificationCodeModel,
            issued.verification_id,
        )

        assert verification is not None
        verification.delivery_status = "sent"
        session.commit()

    def override_confirmation_service():
        with test_session_factory() as session:
            yield FotosVerificationConfirmationRequestService(
                session=session,
                code_service=code_service,
                password_service=password_service,
                rate_limit_service=FotosAuthRateLimitService(
                    session_factory=test_session_factory,
                    secret_key="a" * 64,
                ),
            )

    test_app.dependency_overrides[get_fotos_verification_confirmation_service] = (
        override_confirmation_service
    )

    payload = {
        "organization_code": str(organization["code"]),
        "email": str(user["email"]),
        "code": issued.code,
        "new_password": new_password,
    }

    try:
        with test_session_factory() as session:
            stored_user = session.get(UserModel, user_id)

            assert stored_user is not None
            assert stored_user.password_hash is not None
            assert password_service.verify(
                old_password,
                stored_user.password_hash,
            )

        response = client.post(
            "/api/fotos/auth/password-reset/confirm",
            json=payload,
        )

        assert response.status_code == 200, response.text

        with test_session_factory() as session:
            stored_user = session.get(UserModel, user_id)
            stored_code = session.get(
                FotosVerificationCodeModel,
                issued.verification_id,
            )

            assert stored_user is not None
            assert stored_user.password_hash is not None

            assert password_service.verify(
                new_password,
                stored_user.password_hash,
            )
            assert not password_service.verify(
                old_password,
                stored_user.password_hash,
            )

            assert stored_code is not None
            assert stored_code.consumed_at is not None

        second_response = client.post(
            "/api/fotos/auth/password-reset/confirm",
            json={
                **payload,
                "new_password": "OutraSenha789",
            },
        )

        assert second_response.status_code == 400

        with test_session_factory() as session:
            stored_user = session.get(UserModel, user_id)

            assert stored_user is not None
            assert stored_user.password_hash is not None
            assert password_service.verify(
                new_password,
                stored_user.password_hash,
            )

    finally:
        test_app.dependency_overrides.pop(
            get_fotos_verification_confirmation_service,
            None,
        )
