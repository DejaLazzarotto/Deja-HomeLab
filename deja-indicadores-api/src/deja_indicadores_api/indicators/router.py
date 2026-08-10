from typing import Annotated

from fastapi import APIRouter, Path, Query, Response, status

from deja_indicadores_api.indicators.dependencies import (
    IndicatorServiceDependency,
)
from deja_indicadores_api.indicators.schemas import (
    IndicatorCreate,
    IndicatorResponse,
    IndicatorUpdate,
)

router = APIRouter(prefix="/indicators", tags=["Indicadores"])


IndicatorId = Annotated[
    str,
    Path(
        min_length=36,
        max_length=36,
        description="Identificador UUID do indicador.",
    ),
]

CompanyIdFilter = Annotated[
    str | None,
    Query(
        min_length=36,
        max_length=36,
        description="Filtra os indicadores pelo UUID da empresa.",
    ),
]


@router.get("", response_model=list[IndicatorResponse])
def list_indicators(
    service: IndicatorServiceDependency,
    company_id: CompanyIdFilter = None,
) -> list[IndicatorResponse]:
    """Lista indicadores, opcionalmente filtrados por empresa."""

    return service.list(company_id)


@router.get("/{indicator_id}", response_model=IndicatorResponse)
def get_indicator(
    indicator_id: IndicatorId,
    service: IndicatorServiceDependency,
) -> IndicatorResponse:
    """Consulta um indicador pelo identificador."""

    return service.find_by_id(indicator_id)


@router.post(
    "",
    response_model=IndicatorResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_indicator(
    input_data: IndicatorCreate,
    service: IndicatorServiceDependency,
) -> IndicatorResponse:
    """Cadastra um novo indicador."""

    return service.create(input_data)


@router.put("/{indicator_id}", response_model=IndicatorResponse)
def update_indicator(
    indicator_id: IndicatorId,
    input_data: IndicatorUpdate,
    service: IndicatorServiceDependency,
) -> IndicatorResponse:
    """Atualiza integralmente um indicador."""

    return service.update(indicator_id, input_data)


@router.delete(
    "/{indicator_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_indicator(
    indicator_id: IndicatorId,
    service: IndicatorServiceDependency,
) -> Response:
    """Exclui um indicador."""

    service.delete(indicator_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)