from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import api
from sqlalchemy.exc import DBAPIError

from internal.config import database, settings
from internal.controller.http.router import api_router
from internal.usecase.utils import (
    database_error_handler,
    http_exception_handler,
)


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.DESCRIPTION,
        version=settings.VERSION,
        openapi_url='{0}/openapi.json'.format(settings.DOCS),
        swagger_ui_parameters=settings.SWAGGER_UI_PARAMETERS,
    )

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

    api.add_pagination(app)
    app.include_router(api_router, prefix=settings.API)
    app.add_exception_handler(DBAPIError, database_error_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.dependency_overrides.setdefault(*database.override_session)

    return app
