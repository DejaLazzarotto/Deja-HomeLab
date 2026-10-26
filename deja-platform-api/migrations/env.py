from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from deja_platform_api.chamados.client_users.models import (
    ChamadosClientUserModel,
)
from deja_platform_api.chamados.clients.models import (
    ChamadosClientModel,
)
from deja_platform_api.chamados.tickets.models import (
    ChamadosTicketModel,
)
from deja_platform_api.chamados.tickets.timeline.models import (
    ChamadosTicketTimelineModel,
)
from deja_platform_api.companies.models import CompanyModel
from deja_platform_api.core.config import get_settings
from deja_platform_api.core.database import Base
from deja_platform_api.fotos.curation.job_models import FotosFaceJobModel
from deja_platform_api.indicators.models import IndicatorModel
from deja_platform_api.measurements.models import MeasurementModel
from deja_platform_api.tenant_management.models import (
    EnvironmentModel,
    OrganizationModel,
    TenantModel,
)
from deja_platform_api.user_management.models import UserModel

config = context.config
settings = get_settings()

# A configuração explícita do Alembic tem prioridade.
# Na execução normal, utiliza a conexão configurada na API.
explicit_url = config.attributes.get("database_url_override")

config.set_main_option(
    "sqlalchemy.url",
    explicit_url or settings.database_url,
)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

_registered_models = (
    ChamadosClientModel,
    ChamadosClientUserModel,
    ChamadosTicketModel,
    ChamadosTicketTimelineModel,
    CompanyModel,
    FotosFaceJobModel,
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
        dialect_opts={
            "paramstyle": "named",
        },
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Executa migrations conectadas ao banco configurado."""

    connectable = engine_from_config(
        config.get_section(
            config.config_ini_section,
            {},
        ),
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
