from typing import Annotated

from fastapi import APIRouter, Depends, Path, Response, status

from deja_indicadores_api.authentication.dependencies import (
    require_roles,
)
from deja_indicadores_api.authentication.schemas import (
    AuthenticatedUser,
)
from deja_indicadores_api.chamados.client_users.dependencies import (
    ChamadosClientUserServiceDependency,
)
from deja_indicadores_api.chamados.client_users.schemas import (
    ChamadosClientUserCreate,
    ChamadosClientUserResponse,
    ChamadosClientUserUpdate,
)
from deja_indicadores_api.module_management.dependencies import (
    require_module,
)
from deja_indicadores_api.user_management.models import (
    UserRole,
)

router = APIRouter(
    prefix="/chamados/client-users",
    tags=["Deja Chamados - Usuários de Clientes"],
    dependencies=[Depends(require_module("chamados"))],
)


UserId = Annotated[
    str,
    Path(
        min_length=36,
        max_length=36,
        description="Identificador UUID do usuário.",
    ),
]


ChamadosClientUserAdministrator = Annotated[
    AuthenticatedUser,
    Depends(
        require_roles(
            UserRole.PLATFORM_ADMIN,
            UserRole.ORGANIZATION_ADMIN,
            UserRole.TENANT_ADMIN,
        )
    ),
]


@router.get(
    "/{user_id}",
    response_model=ChamadosClientUserResponse,
)
def get_client_user(
    user_id: UserId,
    service: ChamadosClientUserServiceDependency,
    current_user: ChamadosClientUserAdministrator,
) -> ChamadosClientUserResponse:
    """Consulta o Cliente vinculado ao usuário informado."""

    return service.find_by_user_id(
        user_id,
        current_user,
    )


@router.post(
    "",
    response_model=ChamadosClientUserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_client_user(
    input_data: ChamadosClientUserCreate,
    service: ChamadosClientUserServiceDependency,
    current_user: ChamadosClientUserAdministrator,
) -> ChamadosClientUserResponse:
    """Vincula um usuário client a um Cliente do Chamados."""

    return service.create(
        input_data,
        current_user,
    )


@router.put(
    "/{user_id}",
    response_model=ChamadosClientUserResponse,
)
def update_client_user(
    user_id: UserId,
    input_data: ChamadosClientUserUpdate,
    service: ChamadosClientUserServiceDependency,
    current_user: ChamadosClientUserAdministrator,
) -> ChamadosClientUserResponse:
    """Altera o Cliente vinculado ao usuário."""

    return service.update(
        user_id,
        input_data,
        current_user,
    )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_client_user(
    user_id: UserId,
    service: ChamadosClientUserServiceDependency,
    current_user: ChamadosClientUserAdministrator,
) -> Response:
    """Remove o vínculo do usuário com o Cliente."""

    service.delete(
        user_id,
        current_user,
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )