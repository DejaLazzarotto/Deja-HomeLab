from fastapi import APIRouter

from deja_indicadores_api.companies.router import router as companies_router
from deja_indicadores_api.indicators.router import router as indicators_router

api_router = APIRouter()

api_router.include_router(companies_router)
api_router.include_router(indicators_router)
