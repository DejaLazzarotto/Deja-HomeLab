"""Testes do controle de requisicoes da autenticacao Fotos."""

from datetime import datetime

from sqlalchemy.orm import Session, sessionmaker

from deja_indicadores_api.fotos.authentication.rate_limit_models import (
    FotosAuthRateLimitModel,
)
from deja_indicadores_api.fotos.authentication.rate_limit_repository import (
    FotosAuthRateLimitRepository,
)


def test_rate_limit_blocks_requests_above_limit(
    test_session_factory: sessionmaker[Session],
) -> None:
    """Permite apenas o numero configurado de requisicoes."""

    window_start = datetime(2026, 10, 9, 12, 0, 0)
    subject_hash = "a" * 64

    results = []

    for _ in range(5):
        with test_session_factory() as session:
            repository = FotosAuthRateLimitRepository(session)

            results.append(
                repository.consume(
                    scope="ip",
                    subject_hash=subject_hash,
                    window_start=window_start,
                    limit=3,
                )
            )

    assert results == [True, True, True, False, False]

    with test_session_factory() as session:
        record = (
            session.query(FotosAuthRateLimitModel)
            .filter_by(
                scope="ip",
                subject_hash=subject_hash,
                window_start=window_start,
            )
            .one()
        )

        assert record.request_count == 4


def test_rate_limit_separates_windows_and_subjects(
    test_session_factory: sessionmaker[Session],
) -> None:
    """Mantem contadores independentes por janela, origem e escopo."""

    first_window = datetime(2026, 10, 9, 12, 0, 0)
    second_window = datetime(2026, 10, 9, 12, 10, 0)

    def consume(
        scope: str,
        subject_hash: str,
        window_start: datetime,
    ) -> bool:
        with test_session_factory() as session:
            return FotosAuthRateLimitRepository(session).consume(
                scope=scope,
                subject_hash=subject_hash,
                window_start=window_start,
                limit=2,
            )

    assert consume("ip", "a" * 64, first_window)
    assert consume("ip", "a" * 64, first_window)
    assert not consume("ip", "a" * 64, first_window)

    assert consume("ip", "a" * 64, second_window)
    assert consume("ip", "b" * 64, first_window)
    assert consume("account", "a" * 64, first_window)

    with test_session_factory() as session:
        records = session.query(FotosAuthRateLimitModel).all()

        assert len(records) == 4

        counts = {
            (record.scope, record.subject_hash, record.window_start): record.request_count
            for record in records
        }

        assert counts[("ip", "a" * 64, first_window)] == 3
        assert counts[("ip", "a" * 64, second_window)] == 1
        assert counts[("ip", "b" * 64, first_window)] == 1
        assert counts[("account", "a" * 64, first_window)] == 1


def test_rate_limit_concurrent_requests_in_mysql(
    test_session_factory: sessionmaker[Session],
) -> None:
    """Impede que requisicoes simultaneas ultrapassem o limite."""

    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier

    window_start = datetime(2026, 10, 9, 12, 0, 0)
    subject_hash = "c" * 64
    barrier = Barrier(10)

    def consume() -> bool:
        with test_session_factory() as session:
            repository = FotosAuthRateLimitRepository(session)

            barrier.wait(timeout=15)

            return repository.consume(
                scope="ip",
                subject_hash=subject_hash,
                window_start=window_start,
                limit=3,
            )

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(consume) for _ in range(10)]

        results = [future.result(timeout=30) for future in futures]

    assert results.count(True) == 3
    assert results.count(False) == 7

    with test_session_factory() as session:
        records = (
            session.query(FotosAuthRateLimitModel)
            .filter_by(
                scope="ip",
                subject_hash=subject_hash,
                window_start=window_start,
            )
            .all()
        )

        assert len(records) == 1
        assert records[0].request_count == 4
