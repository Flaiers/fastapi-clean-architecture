from fastapi.middleware.cors import CORSMiddleware

from ..controller.http.router import api_router
from ..utils.applications import FastAPI
from ..utils.events import startup_event
from ..utils.exceptions import (
    validation_exception_handler,
    ValidationException
)
from .config import settings


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    openapi_url=f"{settings.API}/openapi.json"
)

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            str(origin)
            for origin
            in settings.BACKEND_CORS_ORIGINS
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API)
app.add_event_handler(settings.STARTUP, startup_event)
app.add_exception_handler(ValidationException,
                          validation_exception_handler)
app.add_pagination()
