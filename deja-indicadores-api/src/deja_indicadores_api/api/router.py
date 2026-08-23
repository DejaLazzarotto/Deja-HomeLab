from fastapi import APIRouter

from deja_indicadores_api.authentication.router import (
    router as authentication_router,
)
from deja_indicadores_api.chamados.clients.router import (
    router as chamados_clients_router,
)
from deja_indicadores_api.companies.router import (
    router as companies_router,
)
from deja_indicadores_api.dashboards.router import (
    router as dashboards_router,
)
from deja_indicadores_api.indicators.router import (
    router as indicators_router,
)
from deja_indicadores_api.measurements.router import (
    router as measurements_router,
)
from deja_indicadores_api.reports.router import (
    router as reports_router,
)
from deja_indicadores_api.tenant_management.router import (
    router as tenant_management_router,
)
from deja_indicadores_api.user_management.router import (
    router as user_management_router,
)

api_router = APIRouter()

api_router.include_router(authentication_router)
api_router.include_router(chamados_clients_router)
api_router.include_router(companies_router)
api_router.include_router(indicators_router)
api_router.include_router(measurements_router)
api_router.include_router(dashboards_router)
api_router.include_router(reports_router)
api_router.include_router(tenant_management_router)
api_router.include_router(user_management_router)
