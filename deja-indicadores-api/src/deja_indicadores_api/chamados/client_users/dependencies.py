from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from deja_indicadores_api.authentication.authorization import (
    AuthorizationService,
)
from deja_indicadores_api.chamados.client_users.repository import (
    ChamadosClientUserRepository,
)
from deja_indicadores_api.chamados.client_users.service import (
    ChamadosClientUserService,
)
from deja_indicadores_api.chamados.clients.repository import (
    ChamadosClientRepository,
)
from deja_indicadores_api.core.database import get_db_session
from deja_indicadores_api.user_management.repository import (
    UserRepository,
)

DatabaseSession = Annotated[
    Session,
    Depends(get_db_session),
]


def get_chamados_client_user_service(
    session: DatabaseSession,
) -> ChamadosClientUserService:
    """Cria o serviço de vínculos entre usuários e Clientes."""

    return ChamadosClientUserService(
        repository=ChamadosClientUserRepository(session),
        client_repository=ChamadosClientRepository(session),
        user_repository=UserRepository(session),
        authorization_service=AuthorizationService(),
    )


ChamadosClientUserServiceDependency = Annotated[
    ChamadosClientUserService,
    Depends(get_chamados_client_user_service),
]