from fastapi.middleware.cors import CORSMiddleware

from ..config import settings
from ..config.database import override_session
from ..config.events import startup_event
from ..controller.http.router import api_router
from ..usecase.utils import FastAPI, ValidationError, validation_error_handler

__all__ = "create_app"


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.DESCRIPTION,
        openapi_url="{0}/openapi.json".format(settings.API)
    )

    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[
                str(origin)
                for origin in settings.BACKEND_CORS_ORIGINS
            ],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    app.include_router(api_router, prefix=settings.API)
    app.add_event_handler(settings.STARTUP, startup_event)
    app.add_exception_handler(ValidationError, validation_error_handler)
    app.override_dependency(*override_session)
    app.add_pagination()

    return app
