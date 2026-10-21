from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from deja_platform_api.authentication.authorization import (
    AuthorizationService,
)
from deja_platform_api.chamados.clients.repository import (
    ChamadosClientRepository,
)
from deja_platform_api.chamados.clients.service import (
    ChamadosClientService,
)
from deja_platform_api.core.database import get_db_session
from deja_platform_api.tenant_management.repository import (
    EnvironmentRepository,
    TenantRepository,
)

DatabaseSession = Annotated[
    Session,
    Depends(get_db_session),
]


def get_chamados_client_service(
    session: DatabaseSession,
) -> ChamadosClientService:
    """Cria o serviço de clientes para a sessão da requisição."""

    repository = ChamadosClientRepository(session)
    tenant_repository = TenantRepository(session)
    environment_repository = EnvironmentRepository(session)
    authorization_service = AuthorizationService()

    return ChamadosClientService(
        repository,
        tenant_repository,
        environment_repository,
        authorization_service,
    )


ChamadosClientServiceDependency = Annotated[
    ChamadosClientService,
    Depends(get_chamados_client_service),
]
