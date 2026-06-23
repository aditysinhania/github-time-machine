from fastapi import APIRouter

from api.routes.repositories import router as repositories_router
from api.routes.contributors import router as contributors_router
from api.routes.timeline import router as timeline_router
from api.routes.hotspots import router as hotspots_router
from api.routes.ownership import router as ownership_router
from api.routes.health import router as health_router
from api.routes.ai import router as ai_router

api_router = APIRouter()

api_router.include_router(repositories_router)
api_router.include_router(contributors_router)
api_router.include_router(timeline_router)
api_router.include_router(hotspots_router)
api_router.include_router(ownership_router)
api_router.include_router(health_router)
api_router.include_router(ai_router)
