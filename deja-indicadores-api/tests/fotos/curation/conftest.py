from collections.abc import Generator

import pytest
from sqlalchemy import Engine, create_engine
from sqlalchemy.pool import StaticPool

from deja_indicadores_api.core.database import Base
from tests.fotos.media.test_media_api import media_context  # noqa: F401


@pytest.fixture(scope="session")
def test_engine() -> Generator[Engine, None, None]:
    """Executa os contratos da curadoria sem exigir MySQL nesta suíte isolada."""

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    try:
        yield engine
    finally:
        Base.metadata.drop_all(engine)
        engine.dispose()
