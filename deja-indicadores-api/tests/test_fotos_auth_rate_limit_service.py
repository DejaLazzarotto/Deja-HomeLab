"""Testes do servico de rate limiting da autenticacao Fotos."""

from datetime import UTC, datetime

from sqlalchemy.orm import Session, sessionmaker

from deja_indicadores_api.fotos.authentication.rate_limit_models import (
    FotosAuthRateLimitModel,
)
from deja_indicadores_api.fotos.authentication.rate_limit_service import (
    FotosAuthRateLimitService,
)

TEST_SECRET = "fotos-rate-limit-test-secret"
TEST_NOW = datetime(2026, 10, 9, 12, 1, tzinfo=UTC)


def create_service(
    factory: sessionmaker[Session],
) -> FotosAuthRateLimitService:
    return FotosAuthRateLimitService(
        session_factory=factory,
        secret_key=TEST_SECRET,
    )


def test_blocks_after_ten_requests_per_ip(
    test_session_factory: sessionmaker[Session],
) -> None:
    """Bloqueia a origem apos dez solicitacoes na mesma janela."""

    service = create_service(test_session_factory)

    results = [
        service.allow_request(
            client_ip="192.0.2.10",
            organization_code="empresa-a",
            email=f"user{index}@example.com",
            now=TEST_NOW,
        )
        for index in range(12)
    ]

    assert results == [True] * 10 + [False] * 2


def test_blocks_after_three_requests_per_account(
    test_session_factory: sessionmaker[Session],
) -> None:
    """Bloqueia a conta apos tres solicitacoes na mesma janela."""

    service = create_service(test_session_factory)

    results = [
        service.allow_request(
            client_ip=f"192.0.2.{index + 1}",
            organization_code="empresa-a",
            email="pessoa@example.com",
            now=TEST_NOW,
        )
        for index in range(5)
    ]

    assert results == [True, True, True, False, False]


def test_accounts_are_independent_between_organizations(
    test_session_factory: sessionmaker[Session],
) -> None:
    """A mesma conta textual nao compartilha limites entre empresas."""

    service = create_service(test_session_factory)

    for _ in range(3):
        assert service.allow_request(
            client_ip="192.0.2.20",
            organization_code="empresa-a",
            email="pessoa@example.com",
            now=TEST_NOW,
        )

    assert not service.allow_request(
        client_ip="192.0.2.20",
        organization_code="empresa-a",
        email="pessoa@example.com",
        now=TEST_NOW,
    )

    assert service.allow_request(
        client_ip="192.0.2.21",
        organization_code="empresa-b",
        email="pessoa@example.com",
        now=TEST_NOW,
    )


def test_does_not_store_plaintext_identifiers(
    test_session_factory: sessionmaker[Session],
) -> None:
    """Persiste somente hashes, sem dados identificaveis em texto puro."""

    service = create_service(test_session_factory)

    assert service.allow_request(
        client_ip="192.0.2.99",
        organization_code="empresa-privada",
        email="privado@example.com",
        now=TEST_NOW,
    )

    with test_session_factory() as session:
        records = session.query(FotosAuthRateLimitModel).all()

        assert len(records) == 2

        for record in records:
            assert len(record.subject_hash) == 64
            assert all(character in "0123456789abcdef" for character in record.subject_hash)
            assert "192.0.2.99" not in record.subject_hash
            assert "privado@example.com" not in record.subject_hash
            assert "empresa-privada" not in record.subject_hash


def test_confirmation_blocks_after_ten_attempts_per_account(
    test_session_factory: sessionmaker[Session],
) -> None:
    """Bloqueia confirmacoes acima do limite por conta."""

    service = create_service(test_session_factory)

    results = [
        service.allow_confirmation(
            client_ip=f"192.0.2.{index + 1}",
            organization_code="empresa-a",
            email="pessoa@example.com",
            now=TEST_NOW,
        )
        for index in range(12)
    ]

    assert results == [True] * 10 + [False] * 2

    with test_session_factory() as session:
        records = session.query(FotosAuthRateLimitModel).filter_by(scope="confirm_account").all()

        assert len(records) == 1
        assert records[0].request_count == 11


def test_confirmation_blocks_after_thirty_attempts_per_ip(
    test_session_factory: sessionmaker[Session],
) -> None:
    """Bloqueia confirmacoes acima do limite por endereco IP."""

    service = create_service(test_session_factory)

    results = [
        service.allow_confirmation(
            client_ip="192.0.2.50",
            organization_code="empresa-a",
            email=f"pessoa{index}@example.com",
            now=TEST_NOW,
        )
        for index in range(32)
    ]

    assert results == [True] * 30 + [False] * 2

    with test_session_factory() as session:
        records = session.query(FotosAuthRateLimitModel).filter_by(scope="confirm_ip").all()

        assert len(records) == 1
        assert records[0].request_count == 31


def test_confirmation_and_request_limits_are_independent(
    test_session_factory: sessionmaker[Session],
) -> None:
    """Solicitar codigo nao consome limites de confirmacao."""

    service = create_service(test_session_factory)

    for _ in range(3):
        assert service.allow_request(
            client_ip="192.0.2.80",
            organization_code="empresa-a",
            email="pessoa@example.com",
            now=TEST_NOW,
        )

    assert not service.allow_request(
        client_ip="192.0.2.80",
        organization_code="empresa-a",
        email="pessoa@example.com",
        now=TEST_NOW,
    )

    assert service.allow_confirmation(
        client_ip="192.0.2.80",
        organization_code="empresa-a",
        email="pessoa@example.com",
        now=TEST_NOW,
    )

    with test_session_factory() as session:
        records = session.query(FotosAuthRateLimitModel).all()

        counts = {record.scope: record.request_count for record in records}

        assert counts == {
            "ip": 4,
            "account": 4,
            "confirm_ip": 1,
            "confirm_account": 1,
        }
