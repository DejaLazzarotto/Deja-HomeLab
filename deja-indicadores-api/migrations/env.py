from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from deja_indicadores_api.companies.models import CompanyModel
from deja_indicadores_api.core.config import get_settings
from deja_indicadores_api.core.database import Base
from deja_indicadores_api.indicators.models import IndicatorModel
from deja_indicadores_api.measurements.models import MeasurementModel
from deja_indicadores_api.tenant_management.models import (
    EnvironmentModel,
    OrganizationModel,
    TenantModel,
)
from deja_indicadores_api.user_management.models import UserModel

config = context.config
settings = get_settings()

config.set_main_option("sqlalchemy.url", settings.database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

_registered_models = (
    CompanyModel,
    IndicatorModel,
    MeasurementModel,
    OrganizationModel,
    TenantModel,
    EnvironmentModel,
    UserModel,
)


def run_migrations_offline() -> None:
    """Executa migrations sem estabelecer conexão direta com o banco."""

    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Executa migrations conectadas ao banco configurado."""

    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
