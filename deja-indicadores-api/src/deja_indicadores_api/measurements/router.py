from datetime import date
from typing import Annotated

from fastapi import APIRouter, Path, Query, Response, status

from deja_indicadores_api.measurements.dependencies import (
    MeasurementServiceDependency,
)
from deja_indicadores_api.measurements.schemas import (
    MeasurementCreate,
    MeasurementResponse,
    MeasurementUpdate,
)

router = APIRouter(prefix="/measurements", tags=["Coleta Manual de Dados"])

MeasurementId = Annotated[
    str,
    Path(
        min_length=36,
        max_length=36,
        description="Identificador UUID da medição.",
    ),
]

CompanyIdFilter = Annotated[
    str | None,
    Query(
        min_length=36,
        max_length=36,
        description="Filtra as medições pelo UUID da empresa.",
    ),
]

IndicatorIdFilter = Annotated[
    str | None,
    Query(
        min_length=36,
        max_length=36,
        description="Filtra as medições pelo UUID do indicador.",
    ),
]

StartDateFilter = Annotated[
    date | None,
    Query(
        description="Data inicial inclusiva do período de referência.",
    ),
]

EndDateFilter = Annotated[
    date | None,
    Query(
        description="Data final inclusiva do período de referência.",
    ),
]


@router.get("", response_model=list[MeasurementResponse])
def list_measurements(
    service: MeasurementServiceDependency,
    company_id: CompanyIdFilter = None,
    indicator_id: IndicatorIdFilter = None,
    start_date: StartDateFilter = None,
    end_date: EndDateFilter = None,
) -> list[MeasurementResponse]:
    """Lista medições de acordo com os filtros informados."""

    return service.list(
        company_id=company_id,
        indicator_id=indicator_id,
        start_date=start_date,
        end_date=end_date,
    )


@router.get("/{measurement_id}", response_model=MeasurementResponse)
def get_measurement(
    measurement_id: MeasurementId,
    service: MeasurementServiceDependency,
) -> MeasurementResponse:
    """Consulta uma medição pelo identificador."""

    return service.find_by_id(measurement_id)


@router.post(
    "",
    response_model=MeasurementResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_measurement(
    input_data: MeasurementCreate,
    service: MeasurementServiceDependency,
) -> MeasurementResponse:
    """Cadastra uma medição manual."""

    return service.create(input_data)


@router.put(
    "/{measurement_id}",
    response_model=MeasurementResponse,
)
def update_measurement(
    measurement_id: MeasurementId,
    input_data: MeasurementUpdate,
    service: MeasurementServiceDependency,
) -> MeasurementResponse:
    """Atualiza integralmente uma medição manual."""

    return service.update(measurement_id, input_data)


@router.delete(
    "/{measurement_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_measurement(
    measurement_id: MeasurementId,
    service: MeasurementServiceDependency,
) -> Response:
    """Exclui uma medição manual."""

    service.delete(measurement_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)