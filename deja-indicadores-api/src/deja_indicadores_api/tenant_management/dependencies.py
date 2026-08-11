from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from deja_indicadores_api.core.database import get_db_session
from deja_indicadores_api.tenant_management.repository import (
    EnvironmentRepository,
    OrganizationRepository,
    TenantRepository,
)
from deja_indicadores_api.tenant_management.service import (
    EnvironmentService,
    OrganizationService,
    TenantService,
)

DatabaseSession = Annotated[Session, Depends(get_db_session)]


def get_organization_service(
    session: DatabaseSession,
) -> OrganizationService:
    """Cria o serviço de organizações para a sessão da requisição."""

    organization_repository = OrganizationRepository(session)
    tenant_repository = TenantRepository(session)

    return OrganizationService(
        organization_repository,
        tenant_repository,
    )


def get_tenant_service(
    session: DatabaseSession,
) -> TenantService:
    """Cria o serviço de tenants para a sessão da requisição."""

    organization_repository = OrganizationRepository(session)
    tenant_repository = TenantRepository(session)
    environment_repository = EnvironmentRepository(session)

    return TenantService(
        organization_repository,
        tenant_repository,
        environment_repository,
    )


def get_environment_service(
    session: DatabaseSession,
) -> EnvironmentService:
    """Cria o serviço de ambientes para a sessão da requisição."""

    tenant_repository = TenantRepository(session)
    environment_repository = EnvironmentRepository(session)

    return EnvironmentService(
        tenant_repository,
        environment_repository,
    )


OrganizationServiceDependency = Annotated[
    OrganizationService,
    Depends(get_organization_service),
]

TenantServiceDependency = Annotated[
    TenantService,
    Depends(get_tenant_service),
]

EnvironmentServiceDependency = Annotated[
    EnvironmentService,
    Depends(get_environment_service),
]