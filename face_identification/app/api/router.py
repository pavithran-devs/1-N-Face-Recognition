"""APIRouter aggregation."""

from fastapi import APIRouter

from app.api.endpoints.health import router as health_router
from app.api.endpoints.identify import router as identify_router
from app.api.endpoints.import_ import router as import_router
from app.api.endpoints.index import router as index_router
from app.api.endpoints.metrics import router as metrics_router

api_router = APIRouter()

# Register routes
api_router.include_router(health_router)
api_router.include_router(identify_router)
api_router.include_router(import_router)
api_router.include_router(index_router)
api_router.include_router(metrics_router)
