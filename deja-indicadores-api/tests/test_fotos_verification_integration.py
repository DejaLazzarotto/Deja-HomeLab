"""Testes de integracao dos codigos de verificacao do Fotos PWA."""

from datetime import timedelta
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from deja_indicadores_api.fotos.authentication.models import (
    FotosVerificationCodeModel,
    FotosVerificationPurpose,
)
from deja_indicadores_api.fotos.authentication.repository import (
    FotosVerificationCodeRepository,
)
from deja_indicadores_api.fotos.authentication.service import (
    FotosVerificationCodeService,
)
from tests.authentication.test_authentication_api import (
    create_organization,
    create_user,
)


def test_verification_code_persists_in_mysql(
    client: TestClient,
    test_session_factory: sessionmaker[Session],
) -> None:
    """Grava um HMAC e recupera o registro em outra sessao."""

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

    code_service = FotosVerificationCodeService("a" * 64)

    verification_id = str(uuid4())
    user_id = str(user["id"])
    purpose = FotosVerificationPurpose.ACTIVATION
    code = "012345"

    created_at = code_service.utc_now()
    expires_at = created_at + timedelta(minutes=10)

    code_hash = code_service.hash_code(
        verification_id=verification_id,
        user_id=user_id,
        purpose=purpose.value,
        code=code,
    )

    with test_session_factory() as session:
        repository = FotosVerificationCodeRepository(session)

        verification = FotosVerificationCodeModel(
            id=verification_id,
            user_id=user_id,
            purpose=purpose.value,
            code_hash=code_hash,
            expires_at=expires_at,
            attempts=0,
            consumed_at=None,
            created_at=created_at,
        )

        repository.add(verification)
        session.commit()

    with test_session_factory() as session:
        repository = FotosVerificationCodeRepository(session)

        stored = repository.find_latest(
            user_id,
            purpose.value,
        )

        assert stored is not None
        assert stored.id == verification_id
        assert stored.user_id == user_id
        assert stored.purpose == "activation"
        assert stored.code_hash == code_hash
        assert stored.code_hash != code
        assert stored.attempts == 0
        assert stored.consumed_at is None

        assert code_service.verify_code(
            verification_id=stored.id,
            user_id=stored.user_id,
            purpose=stored.purpose,
            code=code,
            expected_hash=stored.code_hash,
        )


def test_verification_issuance_persists_in_mysql(
    client: TestClient,
    test_session_factory: sessionmaker[Session],
) -> None:
    """Emite um codigo usando o servico e persiste no MySQL."""

    from deja_indicadores_api.fotos.authentication.issuance import (
        FotosVerificationIssuanceService,
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
    code_service = FotosVerificationCodeService("a" * 64)

    with test_session_factory() as session:
        issuer = FotosVerificationIssuanceService(
            session,
            code_service,
        )

        issued = issuer.issue(
            user_id=user_id,
            purpose=FotosVerificationPurpose.ACTIVATION,
        )

    with test_session_factory() as session:
        repository = FotosVerificationCodeRepository(session)

        stored = repository.find_latest(
            user_id,
            FotosVerificationPurpose.ACTIVATION.value,
        )

        assert stored is not None
        assert stored.id == issued.verification_id
        assert stored.code_hash != issued.code
        assert stored.attempts == 0
        assert stored.consumed_at is None
        assert stored.expires_at == issued.expires_at

        assert code_service.verify_code(
            verification_id=stored.id,
            user_id=stored.user_id,
            purpose=stored.purpose,
            code=issued.code,
            expected_hash=stored.code_hash,
        )


def test_verification_issuance_enforces_cooldown_in_mysql(
    client: TestClient,
    test_session_factory: sessionmaker[Session],
) -> None:
    """Rejeita segunda emissao antes de sessenta segundos."""

    import pytest
    from sqlalchemy import func, select

    from deja_indicadores_api.fotos.authentication.issuance import (
        FotosVerificationCooldownError,
        FotosVerificationIssuanceService,
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
    code_service = FotosVerificationCodeService("a" * 64)

    with test_session_factory() as session:
        issuer = FotosVerificationIssuanceService(
            session,
            code_service,
        )

        first = issuer.issue(
            user_id=user_id,
            purpose=FotosVerificationPurpose.ACTIVATION,
        )

    with test_session_factory() as session:
        issuer = FotosVerificationIssuanceService(
            session,
            code_service,
        )

        with pytest.raises(FotosVerificationCooldownError):
            issuer.issue(
                user_id=user_id,
                purpose=FotosVerificationPurpose.ACTIVATION,
            )

    with test_session_factory() as session:
        count = session.scalar(
            select(func.count())
            .select_from(FotosVerificationCodeModel)
            .where(
                FotosVerificationCodeModel.user_id == user_id,
                FotosVerificationCodeModel.purpose == "activation",
            )
        )

        stored = FotosVerificationCodeRepository(session).find_latest(user_id, "activation")

        assert count == 1
        assert stored is not None
        assert stored.id == first.verification_id
        assert stored.consumed_at is None

        assert code_service.verify_code(
            verification_id=stored.id,
            user_id=user_id,
            purpose=stored.purpose,
            code=first.code,
            expected_hash=stored.code_hash,
        )


def test_verification_resend_invalidates_previous_code_in_mysql(
    client: TestClient,
    test_session_factory: sessionmaker[Session],
) -> None:
    """Invalida o codigo anterior quando um reenvio e permitido."""

    from datetime import timedelta

    from deja_indicadores_api.fotos.authentication.issuance import (
        FotosVerificationIssuanceService,
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
    code_service = FotosVerificationCodeService("a" * 64)

    with test_session_factory() as session:
        issuer = FotosVerificationIssuanceService(
            session,
            code_service,
        )

        first = issuer.issue(
            user_id=user_id,
            purpose=FotosVerificationPurpose.ACTIVATION,
        )

    original_clock = code_service.utc_now

    code_service.utc_now = lambda: original_clock() + timedelta(seconds=61)

    with test_session_factory() as session:
        issuer = FotosVerificationIssuanceService(
            session,
            code_service,
        )

        second = issuer.issue(
            user_id=user_id,
            purpose=FotosVerificationPurpose.ACTIVATION,
        )

    with test_session_factory() as session:
        first_record = session.get(
            FotosVerificationCodeModel,
            first.verification_id,
        )
        second_record = session.get(
            FotosVerificationCodeModel,
            second.verification_id,
        )

        assert first_record is not None
        assert second_record is not None

        assert first_record.consumed_at is not None
        assert second_record.consumed_at is None

        assert not code_service.is_usable(
            expires_at=first_record.expires_at,
            attempts=first_record.attempts,
            consumed_at=first_record.consumed_at,
            now=code_service.utc_now(),
        )

        assert code_service.verify_code(
            verification_id=second_record.id,
            user_id=user_id,
            purpose=second_record.purpose,
            code=second.code,
            expected_hash=second_record.code_hash,
        )


def test_concurrent_verification_issuance_in_mysql(
    client: TestClient,
    test_session_factory: sessionmaker[Session],
) -> None:
    """Impede duas emissoes simultaneas para o mesmo usuario."""

    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier

    from sqlalchemy import func, select

    from deja_indicadores_api.fotos.authentication.issuance import (
        FotosVerificationCooldownError,
        FotosVerificationIssuanceService,
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
    barrier = Barrier(2)

    def request_code() -> str:
        code_service = FotosVerificationCodeService("a" * 64)

        with test_session_factory() as session:
            issuer = FotosVerificationIssuanceService(
                session,
                code_service,
            )

            barrier.wait(timeout=10)

            try:
                issuer.issue(
                    user_id=user_id,
                    purpose=FotosVerificationPurpose.ACTIVATION,
                )
            except FotosVerificationCooldownError:
                return "cooldown"

            return "issued"

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(request_code) for _ in range(2)]
        results = [future.result(timeout=20) for future in futures]

    assert sorted(results) == ["cooldown", "issued"]

    with test_session_factory() as session:
        count = session.scalar(
            select(func.count())
            .select_from(FotosVerificationCodeModel)
            .where(
                FotosVerificationCodeModel.user_id == user_id,
                FotosVerificationCodeModel.purpose == "activation",
            )
        )

        assert count == 1


def test_verification_confirmation_updates_password_in_mysql(
    client: TestClient,
    test_session_factory: sessionmaker[Session],
) -> None:
    """Define a senha, consome o codigo e impede reutilizacao."""

    import pytest

    from deja_indicadores_api.core.security import PasswordService
    from deja_indicadores_api.fotos.authentication.confirmation import (
        FotosVerificationConfirmationService,
        FotosVerificationInvalidCodeError,
    )
    from deja_indicadores_api.fotos.authentication.issuance import (
        FotosVerificationIssuanceService,
    )
    from deja_indicadores_api.user_management.models import UserModel

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
    code_service = FotosVerificationCodeService("a" * 64)
    password_service = PasswordService()
    new_password = "NovaSenha123"

    with test_session_factory() as session:
        issuer = FotosVerificationIssuanceService(
            session,
            code_service,
        )

        issued = issuer.issue(
            user_id=user_id,
            purpose=FotosVerificationPurpose.ACTIVATION,
        )

    # Simula a aceitacao da mensagem pelo servidor SMTP.
    with test_session_factory() as session:
        stored_code = session.get(
            FotosVerificationCodeModel,
            issued.verification_id,
        )
        assert stored_code is not None
        assert stored_code.delivery_status == "pending"
        stored_code.delivery_status = "sent"
        session.commit()

    with test_session_factory() as session:
        confirmation = FotosVerificationConfirmationService(
            session,
            code_service,
            password_service,
        )

        confirmation.confirm(
            user_id=user_id,
            purpose=FotosVerificationPurpose.ACTIVATION,
            code=issued.code,
            new_password=new_password,
        )

    with test_session_factory() as session:
        stored_user = session.get(UserModel, user_id)
        stored_code = session.get(
            FotosVerificationCodeModel,
            issued.verification_id,
        )

        assert stored_user is not None
        assert stored_user.password_hash is not None
        assert stored_user.password_hash != new_password
        assert password_service.verify(
            new_password,
            stored_user.password_hash,
        )

        assert stored_code is not None
        assert stored_code.consumed_at is not None

    with test_session_factory() as session:
        confirmation = FotosVerificationConfirmationService(
            session,
            code_service,
            password_service,
        )

        with pytest.raises(FotosVerificationInvalidCodeError):
            confirmation.confirm(
                user_id=user_id,
                purpose=FotosVerificationPurpose.ACTIVATION,
                code=issued.code,
                new_password="OutraSenha123",
            )

    with test_session_factory() as session:
        stored_user = session.get(UserModel, user_id)

        assert stored_user is not None
        assert stored_user.password_hash is not None
        assert password_service.verify(
            new_password,
            stored_user.password_hash,
        )


def test_verification_five_invalid_attempts_in_mysql(
    client: TestClient,
    test_session_factory: sessionmaker[Session],
) -> None:
    """Bloqueia o codigo apos cinco tentativas incorretas."""

    import pytest

    from deja_indicadores_api.core.security import PasswordService
    from deja_indicadores_api.fotos.authentication.confirmation import (
        FotosVerificationConfirmationService,
        FotosVerificationInvalidCodeError,
    )
    from deja_indicadores_api.fotos.authentication.issuance import (
        FotosVerificationIssuanceService,
    )
    from deja_indicadores_api.user_management.models import UserModel

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
    code_service = FotosVerificationCodeService("a" * 64)
    password_service = PasswordService()

    with test_session_factory() as session:
        issued = FotosVerificationIssuanceService(
            session,
            code_service,
        ).issue(
            user_id=user_id,
            purpose=FotosVerificationPurpose.ACTIVATION,
        )

    # Simula a aceitacao da mensagem pelo servidor SMTP.
    with test_session_factory() as session:
        stored_code = session.get(
            FotosVerificationCodeModel,
            issued.verification_id,
        )
        assert stored_code is not None
        assert stored_code.delivery_status == "pending"
        stored_code.delivery_status = "sent"
        session.commit()

    invalid_code = "000000" if issued.code != "000000" else "999999"

    for attempt in range(1, 6):
        with test_session_factory() as session:
            confirmation = FotosVerificationConfirmationService(
                session,
                code_service,
                password_service,
            )

            with pytest.raises(FotosVerificationInvalidCodeError):
                confirmation.confirm(
                    user_id=user_id,
                    purpose=FotosVerificationPurpose.ACTIVATION,
                    code=invalid_code,
                    new_password="NovaSenha123",
                )

        with test_session_factory() as session:
            stored_code = session.get(
                FotosVerificationCodeModel,
                issued.verification_id,
            )

            assert stored_code is not None
            assert stored_code.attempts == attempt
            assert stored_code.consumed_at is None

    with test_session_factory() as session:
        confirmation = FotosVerificationConfirmationService(
            session,
            code_service,
            password_service,
        )

        with pytest.raises(FotosVerificationInvalidCodeError):
            confirmation.confirm(
                user_id=user_id,
                purpose=FotosVerificationPurpose.ACTIVATION,
                code=issued.code,
                new_password="NovaSenha123",
            )

    with test_session_factory() as session:
        stored_code = session.get(
            FotosVerificationCodeModel,
            issued.verification_id,
        )
        stored_user = session.get(UserModel, user_id)

        assert stored_code is not None
        assert stored_code.attempts == 5

        assert stored_user is not None
        assert stored_user.password_hash is None


def test_verification_expired_code_in_mysql(
    client: TestClient,
    test_session_factory: sessionmaker[Session],
) -> None:
    """Rejeita codigo expirado sem modificar a senha."""

    import pytest

    from deja_indicadores_api.core.security import PasswordService
    from deja_indicadores_api.fotos.authentication.confirmation import (
        FotosVerificationConfirmationService,
        FotosVerificationInvalidCodeError,
    )
    from deja_indicadores_api.fotos.authentication.issuance import (
        FotosVerificationIssuanceService,
    )
    from deja_indicadores_api.user_management.models import UserModel

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
    code_service = FotosVerificationCodeService("a" * 64)

    with test_session_factory() as session:
        issued = FotosVerificationIssuanceService(
            session,
            code_service,
        ).issue(
            user_id=user_id,
            purpose=FotosVerificationPurpose.ACTIVATION,
        )

    # Simula a aceitacao da mensagem pelo servidor SMTP.
    with test_session_factory() as session:
        stored_code = session.get(
            FotosVerificationCodeModel,
            issued.verification_id,
        )
        assert stored_code is not None
        assert stored_code.delivery_status == "pending"
        stored_code.delivery_status = "sent"
        session.commit()

    with test_session_factory() as session:
        stored_code = session.get(
            FotosVerificationCodeModel,
            issued.verification_id,
        )

        assert stored_code is not None

        stored_code.expires_at = code_service.utc_now() - timedelta(seconds=1)

        session.commit()

    with test_session_factory() as session:
        confirmation = FotosVerificationConfirmationService(
            session,
            code_service,
            PasswordService(),
        )

        with pytest.raises(FotosVerificationInvalidCodeError):
            confirmation.confirm(
                user_id=user_id,
                purpose=FotosVerificationPurpose.ACTIVATION,
                code=issued.code,
                new_password="NovaSenha123",
            )

    with test_session_factory() as session:
        stored_code = session.get(
            FotosVerificationCodeModel,
            issued.verification_id,
        )
        stored_user = session.get(UserModel, user_id)

        assert stored_code is not None
        assert stored_code.attempts == 0
        assert stored_code.consumed_at is None

        assert stored_user is not None
        assert stored_user.password_hash is None


def test_concurrent_verification_confirmation_in_mysql(
    client: TestClient,
    test_session_factory: sessionmaker[Session],
) -> None:
    """Permite apenas uma confirmacao do mesmo codigo."""

    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier

    from deja_indicadores_api.core.security import PasswordService
    from deja_indicadores_api.fotos.authentication.confirmation import (
        FotosVerificationConfirmationService,
        FotosVerificationInvalidCodeError,
    )
    from deja_indicadores_api.fotos.authentication.issuance import (
        FotosVerificationIssuanceService,
    )
    from deja_indicadores_api.user_management.models import UserModel

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
    code_service = FotosVerificationCodeService("a" * 64)

    with test_session_factory() as session:
        issued = FotosVerificationIssuanceService(
            session,
            code_service,
        ).issue(
            user_id=user_id,
            purpose=FotosVerificationPurpose.ACTIVATION,
        )

    # Simula a aceitacao da mensagem pelo servidor SMTP.
    with test_session_factory() as session:
        stored_code = session.get(
            FotosVerificationCodeModel,
            issued.verification_id,
        )
        assert stored_code is not None
        assert stored_code.delivery_status == "pending"
        stored_code.delivery_status = "sent"
        session.commit()

    barrier = Barrier(2)

    def confirm_code(password: str) -> str:
        with test_session_factory() as session:
            confirmation = FotosVerificationConfirmationService(
                session,
                FotosVerificationCodeService("a" * 64),
                PasswordService(),
            )

            barrier.wait(timeout=10)

            try:
                confirmation.confirm(
                    user_id=user_id,
                    purpose=FotosVerificationPurpose.ACTIVATION,
                    code=issued.code,
                    new_password=password,
                )
            except FotosVerificationInvalidCodeError:
                return "rejected"

            return "confirmed"

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [
            executor.submit(confirm_code, "SenhaPrimeira123"),
            executor.submit(confirm_code, "SenhaSegunda123"),
        ]

        results = [future.result(timeout=30) for future in futures]

    assert sorted(results) == ["confirmed", "rejected"]

    with test_session_factory() as session:
        stored_user = session.get(UserModel, user_id)
        stored_code = session.get(
            FotosVerificationCodeModel,
            issued.verification_id,
        )

        assert stored_user is not None
        assert stored_user.password_hash is not None

        password_service = PasswordService()

        first_password_valid = password_service.verify(
            "SenhaPrimeira123",
            stored_user.password_hash,
        )
        second_password_valid = password_service.verify(
            "SenhaSegunda123",
            stored_user.password_hash,
        )

        assert first_password_valid != second_password_valid

        assert stored_code is not None
        assert stored_code.consumed_at is not None
        assert stored_code.attempts == 0


@pytest.mark.parametrize("delivery_status", ["pending", "failed"])
def test_verification_rejects_undelivered_code_in_mysql(
    client: TestClient,
    test_session_factory: sessionmaker[Session],
    delivery_status: str,
) -> None:
    """Rejeita no MySQL codigos ainda nao enviados ou com falha."""

    from deja_indicadores_api.core.security import PasswordService
    from deja_indicadores_api.fotos.authentication.confirmation import (
        FotosVerificationConfirmationService,
        FotosVerificationInvalidCodeError,
    )
    from deja_indicadores_api.fotos.authentication.issuance import (
        FotosVerificationIssuanceService,
    )
    from deja_indicadores_api.user_management.models import UserModel

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
        stored_code = session.get(
            FotosVerificationCodeModel,
            issued.verification_id,
        )

        assert stored_code is not None
        assert stored_code.delivery_status == "pending"

        stored_code.delivery_status = delivery_status
        session.commit()

    with test_session_factory() as session:
        confirmation = FotosVerificationConfirmationService(
            session,
            code_service,
            PasswordService(),
        )

        with pytest.raises(FotosVerificationInvalidCodeError):
            confirmation.confirm(
                user_id=user_id,
                purpose=FotosVerificationPurpose.ACTIVATION,
                code=issued.code,
                new_password="NovaSenha123",
            )

    with test_session_factory() as session:
        stored_user = session.get(UserModel, user_id)
        stored_code = session.get(
            FotosVerificationCodeModel,
            issued.verification_id,
        )

        assert stored_user is not None
        assert stored_user.password_hash is None

        assert stored_code is not None
        assert stored_code.delivery_status == delivery_status
        assert stored_code.attempts == 0
        assert stored_code.consumed_at is None


@pytest.mark.parametrize(
    ("initial_status", "new_status", "expected_result"),
    [
        ("pending", "sent", True),
        ("pending", "failed", True),
        ("sent", "failed", False),
        ("failed", "sent", False),
    ],
)
def test_delivery_status_transitions_in_mysql(
    client: TestClient,
    test_session_factory: sessionmaker[Session],
    initial_status: str,
    new_status: str,
    expected_result: bool,
) -> None:
    """Garante transicoes controladas do estado de entrega."""

    from deja_indicadores_api.fotos.authentication.issuance import (
        FotosVerificationIssuanceService,
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
        stored = session.get(
            FotosVerificationCodeModel,
            issued.verification_id,
        )
        assert stored is not None

        stored.delivery_status = initial_status
        session.commit()

    with test_session_factory() as session:
        repository = FotosVerificationCodeRepository(session)

        updated = repository.update_delivery_status(
            issued.verification_id,
            new_status,
        )

        assert updated is expected_result
        session.commit()

    with test_session_factory() as session:
        stored = session.get(
            FotosVerificationCodeModel,
            issued.verification_id,
        )

        assert stored is not None
        expected_status = new_status if expected_result else initial_status
        assert stored.delivery_status == expected_status


def test_delivery_status_rejects_invalid_updates_in_mysql(
    client: TestClient,
    test_session_factory: sessionmaker[Session],
) -> None:
    """Nao altera entregas com identificador ou estado invalido."""

    from deja_indicadores_api.fotos.authentication.issuance import (
        FotosVerificationIssuanceService,
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

    code_service = FotosVerificationCodeService("a" * 64)

    with test_session_factory() as session:
        issued = FotosVerificationIssuanceService(
            session,
            code_service,
        ).issue(
            user_id=str(user["id"]),
            purpose=FotosVerificationPurpose.ACTIVATION,
        )

    with test_session_factory() as session:
        repository = FotosVerificationCodeRepository(session)

        assert not repository.update_delivery_status(
            "00000000-0000-0000-0000-000000000000",
            "sent",
        )

        with pytest.raises(ValueError):
            repository.update_delivery_status(
                issued.verification_id,
                "delivered",
            )

        session.commit()

    with test_session_factory() as session:
        stored = session.get(
            FotosVerificationCodeModel,
            issued.verification_id,
        )

        assert stored is not None
        assert stored.delivery_status == "pending"
        assert stored.attempts == 0
        assert stored.consumed_at is None
