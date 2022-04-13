from fastapi.middleware.cors import CORSMiddleware

from internal.config import database, events, settings
from internal.controller.http.router import api_router
from internal.usecase.utils import (
    FastAPI,
    ValidationError,
    validation_error_handler,
)


def create_app() -> FastAPI:
    app = FastAPI(settings=settings)

    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[
                str(origin)
                for origin in settings.BACKEND_CORS_ORIGINS
            ],
            allow_credentials=True,
            allow_methods=['*'],
            allow_headers=['*'],
        )

    app.include_router(api_router, prefix=settings.API)
    app.add_event_handler(settings.STARTUP, events.startup_event(settings))
    app.add_exception_handler(ValidationError, validation_error_handler)
    app.override_dependency(*database.override_session)
    app.add_pagination()

    return app
