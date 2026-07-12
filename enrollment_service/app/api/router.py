"""Root API router — aggregates all v1 sub-routers."""
from fastapi import APIRouter

from app.api.v1 import candidates, embedding, export, face, health
from app.api.v1 import import_ as import_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(health.router)
api_router.include_router(candidates.router)
api_router.include_router(face.router)
api_router.include_router(embedding.router)
api_router.include_router(export.router)
api_router.include_router(import_router.router)
