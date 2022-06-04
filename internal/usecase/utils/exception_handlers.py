from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import DBAPIError


async def database_error_handler(
    _: Request, exc: DBAPIError,
) -> JSONResponse:
    detail = str(exc.orig).split('DETAIL:  ')[-1].rstrip('.')
    return JSONResponse(
        content={'successful': False, 'detail': detail},
        status_code=status.HTTP_400_BAD_REQUEST,
    )


async def http_exception_handler(
    _: Request, exc: HTTPException,
) -> JSONResponse:
    response = JSONResponse(
        content={'successful': False, 'detail': exc.detail},
        status_code=exc.status_code,
    )
    if exc.headers is not None:
        response.init_headers(exc.headers)

    return response