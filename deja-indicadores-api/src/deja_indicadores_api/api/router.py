from fastapi import APIRouter

from deja_indicadores_api.companies.router import router as companies_router

api_router = APIRouter()

api_router.include_router(companies_router)
