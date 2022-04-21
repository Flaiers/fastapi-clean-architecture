from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import DBAPIError


async def database_error_handler(
    _: Request, exc: DBAPIError,
) -> JSONResponse:
    detail = str(exc.orig).split('DETAIL:  ')[-1].replace('.', '')
    return JSONResponse(
        content={'detail': detail},
        status_code=400,
    )
