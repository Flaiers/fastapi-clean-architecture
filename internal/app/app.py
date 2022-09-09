from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import api
from sqlalchemy.exc import DBAPIError, NoResultFound

from internal.config import database, events, settings
from internal.controller.amqp.router import rpc_router
from internal.controller.http.router import api_router
from internal.usecase.utils import (
    database_error_handler,
    database_not_found_handler,
    http_exception_handler,
)
from pkg.rabbitmq.rpc import RPCClient, RPCServer


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.DESCRIPTION,
        version=settings.VERSION,
        openapi_url='{0}/openapi.json'.format(settings.DOCS),
        swagger_ui_parameters=settings.SWAGGER_UI_PARAMETERS,
    )
    server = RPCServer(settings.RABBITMQ_URI)
    client = RPCClient(settings.RABBITMQ_URI, app.state)

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
    server.include_router(rpc_router, prefix=settings.RPC)
    app.dependency_overrides.setdefault(*database.override_session)

    app.add_exception_handler(DBAPIError, database_error_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(NoResultFound, database_not_found_handler)
    app.add_event_handler(settings.STARTUP, events.startup_rpc_server(server))
    app.add_event_handler(settings.STARTUP, events.startup_rpc_client(client))
    app.add_event_handler(settings.SHUTDOWN, events.shutdown_rpc_client(client))

    return app
