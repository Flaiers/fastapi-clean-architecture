from fastapi import APIRouter

from . import applications, health

router = APIRouter()
router.include_router(
    applications.router,
    prefix='/applications',
    tags=['applications'],
)
router.include_router(
    health.router,
    prefix='/health',
    tags=['health'],
)
