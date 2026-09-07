from collections.abc import Generator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine, delete
from sqlalchemy.orm import Session, sessionmaker

from deja_indicadores_api.chamados.clients.models import (
    ChamadosClientModel,
)
from deja_indicadores_api.chamados.tickets.timeline.models import (
    ChamadosTicketTimelineModel,
)
from deja_indicadores_api.chamados.tickets.models import (
    ChamadosTicketModel,
)
from deja_indicadores_api.companies.models import CompanyModel
from deja_indicadores_api.core.config import (
    Settings,
    get_settings,
)
from deja_indicadores_api.core.database import (
    Base,
    get_db_session,
)
from deja_indicadores_api.indicators.models import IndicatorModel
from deja_indicadores_api.main import create_app
from deja_indicadores_api.measurements.models import (
    MeasurementModel,
)
from deja_indicadores_api.module_management.models import (
    ModuleModel,
    OrganizationModuleModel,
)
from deja_indicadores_api.tenant_management.models import (
    EnvironmentModel,
    OrganizationModel,
    TenantModel,
)
from deja_indicadores_api.user_management.models import UserModel


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


def clear_database(
    test_session_factory: sessionmaker[Session],
) -> None:
    """Remove os registros respeitando a ordem das chaves estrangeiras."""

    with test_session_factory() as session:
        session.execute(delete(OrganizationModuleModel))
        session.execute(delete(MeasurementModel))
        session.execute(delete(IndicatorModel))
        session.execute(delete(CompanyModel))
        session.execute(delete(ChamadosTicketTimelineModel))
        session.execute(delete(ChamadosTicketModel))
        session.execute(delete(ChamadosClientModel))
        session.execute(delete(UserModel))
        session.execute(delete(EnvironmentModel))
        session.execute(delete(TenantModel))
        session.execute(delete(OrganizationModel))
        session.execute(delete(ModuleModel))
        session.commit()


@pytest.fixture(autouse=True)
def clean_database(
    test_session_factory: sessionmaker[Session],
) -> Generator[None, None, None]:
    """Garante tabelas vazias antes e depois de cada teste."""

    clear_database(test_session_factory)

    yield

    clear_database(test_session_factory)


@pytest.fixture()
def test_app(
    test_session_factory: sessionmaker[Session],
    test_settings: Settings,
) -> Generator[FastAPI, None, None]:
    """Cria uma aplicação com as dependências substituídas para testes."""

    app = create_app()
    app.state.test_session_factory = test_session_factory

    def override_get_db_session() -> Generator[Session, None, None]:
        session = test_session_factory()

        try:
            yield session
        finally:
            session.close()

    def override_get_settings() -> Settings:
        return test_settings

    app.dependency_overrides[get_db_session] = override_get_db_session
    app.dependency_overrides[get_settings] = override_get_settings

    try:
        yield app
    finally:
        app.dependency_overrides.clear()


@pytest.fixture()
def client(
    test_app: FastAPI,
) -> Generator[TestClient, None, None]:
    """Fornece um cliente HTTP conectado à aplicação isolada."""

    with TestClient(test_app) as test_client:
        yield test_client