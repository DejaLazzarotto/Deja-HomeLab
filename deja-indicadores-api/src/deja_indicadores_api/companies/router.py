from typing import Annotated

from fastapi import APIRouter, Path, Response, status

from deja_indicadores_api.companies.dependencies import CompanyServiceDependency
from deja_indicadores_api.companies.schemas import (
    CompanyCreate,
    CompanyResponse,
    CompanyUpdate,
)

router = APIRouter(prefix="/companies", tags=["Empresas"])

CompanyId = Annotated[
    str,
    Path(
        min_length=36,
        max_length=36,
        description="Identificador UUID da empresa.",
    ),
]


@router.get("", response_model=list[CompanyResponse])
def list_companies(
    service: CompanyServiceDependency,
) -> list[CompanyResponse]:
    """Lista todas as empresas cadastradas."""

    return service.list()


@router.get("/{company_id}", response_model=CompanyResponse)
def get_company(
    company_id: CompanyId,
    service: CompanyServiceDependency,
) -> CompanyResponse:
    """Consulta uma empresa pelo identificador."""

    return service.find_by_id(company_id)


@router.post(
    "",
    response_model=CompanyResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_company(
    input_data: CompanyCreate,
    service: CompanyServiceDependency,
) -> CompanyResponse:
    """Cadastra uma nova empresa."""

    return service.create(input_data)


@router.put("/{company_id}", response_model=CompanyResponse)
def update_company(
    company_id: CompanyId,
    input_data: CompanyUpdate,
    service: CompanyServiceDependency,
) -> CompanyResponse:
    """Atualiza integralmente uma empresa."""

    return service.update(company_id, input_data)


@router.delete(
    "/{company_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_company(
    company_id: CompanyId,
    service: CompanyServiceDependency,
) -> Response:
    """Exclui uma empresa."""

    service.delete(company_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)