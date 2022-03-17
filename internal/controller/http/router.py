from fastapi import APIRouter

from . import v1  # noqa: WPS300

api_router = APIRouter()
api_router.include_router(v1.router, prefix='/v1')
