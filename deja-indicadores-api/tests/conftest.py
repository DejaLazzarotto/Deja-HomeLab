from collections.abc import Generator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine, delete
from sqlalchemy.orm import Session, sessionmaker

from deja_indicadores_api.companies.models import CompanyModel
from deja_indicadores_api.core.config import Settings
from deja_indicadores_api.core.database import Base, get_db_session
from deja_indicadores_api.indicators.models import IndicatorModel
from deja_indicadores_api.main import create_app


@pytest.fixture(scope="session")
def test_settings() -> Settings:
    """Carrega e valida exclusivamente as configurações de testes."""

    settings = Settings(_env_file=".env.test")

    if settings.app_env != "testing":
        pytest.exit(
            "Os testes exigem APP_ENV=testing no arquivo .env.test.",
            returncode=1,
        )

    if not settings.db_name.endswith("_test"):
        pytest.exit(
            "O banco usado pelos testes deve possuir o sufixo '_test'.",
            returncode=1,
        )

    return settings


@pytest.fixture(scope="session")
def test_engine(
    test_settings: Settings,
) -> Generator[Engine, None, None]:
    """Cria a engine vinculada exclusivamente ao banco MySQL de testes."""

    engine = create_engine(
        test_settings.database_url,
        pool_pre_ping=True,
        pool_recycle=3600,
    )

    Base.metadata.create_all(bind=engine)

    try:
        yield engine
    finally:
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture()
def test_session_factory(
    test_engine: Engine,
) -> sessionmaker[Session]:
    """Cria sessões SQLAlchemy exclusivas para os testes."""

    return sessionmaker(
        bind=test_engine,
        autoflush=False,
        expire_on_commit=False,
    )


@pytest.fixture(autouse=True)
def clean_database(
    test_session_factory: sessionmaker[Session],
) -> Generator[None, None, None]:
    """Garante tabelas vazias antes e depois de cada teste."""

    with test_session_factory() as session:
        session.execute(delete(IndicatorModel))
        session.execute(delete(CompanyModel))
        session.commit()

    yield

    with test_session_factory() as session:
        session.execute(delete(IndicatorModel))
        session.execute(delete(CompanyModel))
        session.commit()


@pytest.fixture()
def test_app(
    test_session_factory: sessionmaker[Session],
) -> Generator[FastAPI, None, None]:
    """Cria uma aplicação com a sessão de produção substituída pela de testes."""

    app = create_app()

    def override_get_db_session() -> Generator[Session, None, None]:
        session = test_session_factory()

        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db_session] = override_get_db_session

    try:
        yield app
    finally:
        app.dependency_overrides.clear()


@pytest.fixture()
def client(test_app: FastAPI) -> Generator[TestClient, None, None]:
    """Fornece um cliente HTTP conectado à aplicação isolada."""

    with TestClient(test_app) as test_client:
        yield test_client
