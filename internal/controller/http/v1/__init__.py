from fastapi import APIRouter

from . import applications

router = APIRouter()
router.include_router(
    applications.router,
    prefix='/applications',
    tags=['applications'],
)
