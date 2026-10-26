"""Testes de concorrência real da fila facial usando MySQL/InnoDB."""

import pytest
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker

import tests.conftest  # noqa: F401  # Registra os modelos SQLAlchemy da plataforma.
from deja_platform_api.core.config import Settings
from deja_platform_api.core.database import Base
from deja_platform_api.fotos.curation.job_repository import FotosFaceJobRepository

REQUIRED_TABLES = {
    "organizations",
    "tenants",
    "environments",
    "users",
    "fotos_albums",
    "fotos_media",
    "fotos_face_jobs",
}


@pytest.fixture()
def mysql_face_session_factory():
    """Conecta exclusivamente ao banco MySQL autorizado para homologação."""

    settings = Settings(_env_file=".env.test")

    if settings.app_env != "testing":
        pytest.fail("Ambiente de testes não autorizado.")

    engine = create_engine(
        settings.database_url,
        pool_pre_ping=True,
        connect_args={"connect_timeout": 5},
    )

    try:
        with engine.connect() as connection:
            database = connection.scalar(text("SELECT DATABASE()"))

            if engine.dialect.name != "mysql" or database != "deja_indicadores_test":
                pytest.fail(f"Banco não autorizado para homologação: {database}")

            existing = set(inspect(connection).get_table_names())

            if existing != {"alembic_version"}:
                pytest.fail(
                    "O banco contém tabelas inesperadas. Nenhuma estrutura será modificada."
                )

        yield sessionmaker(
            bind=engine,
            autoflush=False,
            expire_on_commit=False,
        )

    finally:
        engine.dispose()


@pytest.fixture()
def mysql_face_tables(mysql_face_session_factory):
    """Cria e remove exclusivamente as tabelas desta homologação."""

    engine = mysql_face_session_factory.kw["bind"]
    created = []

    tables = [table for table in Base.metadata.sorted_tables if table.name in REQUIRED_TABLES]

    if {table.name for table in tables} != REQUIRED_TABLES:
        pytest.fail("Estrutura incompleta para homologação.")

    try:
        for table in tables:
            with engine.begin() as connection:
                table.create(bind=connection, checkfirst=False)
            created.append(table)

        yield mysql_face_session_factory

    finally:
        errors = []

        for table in reversed(created):
            try:
                with engine.begin() as connection:
                    table.drop(bind=connection, checkfirst=False)
            except Exception as exc:
                errors.append(f"{table.name}: {exc}")

        if errors:
            pytest.fail("Falha na limpeza das tabelas de homologação: " + "; ".join(errors))


def test_claim_next_skips_locked_photo(mysql_face_tables):
    """Valida duas reservas concorrentes no MySQL/InnoDB real."""
    from uuid import uuid4

    from sqlalchemy import insert

    from deja_platform_api.fotos.curation.job_models import FotosFaceJobModel
    from deja_platform_api.fotos.media.models import FotosMediaModel

    factory = mysql_face_tables
    engine = factory.kw["bind"]

    organization_id = str(uuid4())
    tenant_id = str(uuid4())
    environment_id = str(uuid4())
    media_id = str(uuid4())
    job_id = str(uuid4())

    with engine.begin() as connection:
        connection.execute(
            insert(Base.metadata.tables["organizations"]),
            {
                "id": organization_id,
                "code": "VIVARO-TEST",
                "name": "VIVARO Homologacao",
            },
        )
        connection.execute(
            insert(Base.metadata.tables["tenants"]),
            {
                "id": tenant_id,
                "organization_id": organization_id,
                "name": "Tenant Homologacao",
            },
        )
        connection.execute(
            insert(Base.metadata.tables["environments"]),
            {
                "id": environment_id,
                "tenant_id": tenant_id,
                "name": "Ambiente Homologacao",
            },
        )
        connection.execute(
            insert(FotosMediaModel.__table__),
            {
                "id": media_id,
                "organization_id": organization_id,
                "tenant_id": tenant_id,
                "environment_id": environment_id,
                "original_name": "teste.jpg",
                "source_content_type": "image/jpeg",
                "source_file_size": 100,
                "source_checksum_sha256": "a" * 64,
                "media_type": "image",
                "content_type": "image/jpeg",
                "file_size": 100,
                "checksum_sha256": "a" * 64,
                "original_storage_key": "homologacao/teste.jpg",
                "processing_status": "ready",
            },
        )
        connection.execute(
            insert(FotosFaceJobModel.__table__),
            {
                "id": job_id,
                "media_id": media_id,
                "organization_id": organization_id,
                "tenant_id": tenant_id,
                "environment_id": environment_id,
                "status": "pending",
            },
        )

    with factory() as first, factory() as second:
        try:
            first_job = FotosFaceJobRepository(first).claim_next()

            assert first_job is not None
            assert first_job.id == job_id
            assert first_job.status == "processing"

            # Mantém o bloqueio da primeira transação ativo.
            second_job = FotosFaceJobRepository(second).claim_next()

            assert second_job is None, "O segundo worker reservou uma fotografia bloqueada."

            first.commit()
            second.rollback()

            current = second.get(FotosFaceJobModel, job_id)
            assert current is not None
            assert current.status == "processing"
            assert current.claim_token == first_job.claim_token

        finally:
            first.rollback()
            second.rollback()
