from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Response, status

from deja_indicadores_api.authentication.dependencies import require_roles
from deja_indicadores_api.authentication.schemas import AuthenticatedUser
from deja_indicadores_api.companies.dependencies import CompanyServiceDependency
from deja_indicadores_api.companies.schemas import (
    CompanyCreate,
    CompanyResponse,
    CompanyUpdate,
)
from deja_indicadores_api.user_management.models import UserRole

router = APIRouter(prefix="/companies", tags=["Empresas"])

CompanyId = Annotated[
    str,
    Path(
        min_length=36,
        max_length=36,
        description="Identificador UUID da empresa.",
    ),
]

OrganizationFilter = Annotated[
    str | None,
    Query(
        min_length=36,
        max_length=36,
        description="Filtra empresas pela organização.",
    ),
]

TenantFilter = Annotated[
    str | None,
    Query(
        min_length=36,
        max_length=36,
        description="Filtra empresas pelo tenant.",
    ),
]

EnvironmentFilter = Annotated[
    str | None,
    Query(
        min_length=36,
        max_length=36,
        description="Filtra empresas pelo ambiente.",
    ),
]

CompanyReader = Annotated[
    AuthenticatedUser,
    Depends(
        require_roles(
            UserRole.PLATFORM_ADMIN,
            UserRole.ORGANIZATION_ADMIN,
            UserRole.TENANT_ADMIN,
            UserRole.MANAGER,
            UserRole.ANALYST,
            UserRole.VIEWER,
        )
    ),
]

CompanyManager = Annotated[
    AuthenticatedUser,
    Depends(
        require_roles(
            UserRole.PLATFORM_ADMIN,
            UserRole.ORGANIZATION_ADMIN,
            UserRole.TENANT_ADMIN,
            UserRole.MANAGER,
        )
    ),
]


@router.get("", response_model=list[CompanyResponse])
def list_companies(
    service: CompanyServiceDependency,
    current_user: CompanyReader,
    organization_id: OrganizationFilter = None,
    tenant_id: TenantFilter = None,
    environment_id: EnvironmentFilter = None,
) -> list[CompanyResponse]:
    """Lista empresas dentro do escopo permitido."""

    return service.list(
        current_user,
        organization_id=organization_id,
        tenant_id=tenant_id,
        environment_id=environment_id,
    )


@router.get("/{company_id}", response_model=CompanyResponse)
def get_company(
    company_id: CompanyId,
    service: CompanyServiceDependency,
    current_user: CompanyReader,
) -> CompanyResponse:
    """Consulta uma empresa dentro do escopo permitido."""

    return service.find_by_id(company_id, current_user)


@router.post(
    "",
    response_model=CompanyResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_company(
    input_data: CompanyCreate,
    service: CompanyServiceDependency,
    current_user: CompanyManager,
) -> CompanyResponse:
    """Cadastra uma empresa dentro do escopo permitido."""

    return service.create(input_data, current_user)


@router.put("/{company_id}", response_model=CompanyResponse)
def update_company(
    company_id: CompanyId,
    input_data: CompanyUpdate,
    service: CompanyServiceDependency,
    current_user: CompanyManager,
) -> CompanyResponse:
    """Atualiza integralmente uma empresa dentro do escopo permitido."""

    return service.update(
        company_id,
        input_data,
        current_user,
    )


@router.delete(
    "/{company_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_company(
    company_id: CompanyId,
    service: CompanyServiceDependency,
    current_user: CompanyManager,
) -> Response:
    """Exclui uma empresa dentro do escopo permitido."""

    service.delete(company_id, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
