from fastapi.responses import JSONResponse
from fastapi import Request

from sqlalchemy.exc import DBAPIError

from typing import Any, Dict


__all__ = ["ValidationException", "validation_exception_handler"]


class ValidationException(Exception):

    def __init__(
        self,
        error: DBAPIError,
        status_code: int = 400,
        headers: Dict[str, Any] | None = None,
    ) -> None:
        self.detail = str(error.orig).split("DETAIL:  ")[-1]
        self.status_code = status_code
        self.headers = headers


async def validation_exception_handler(
    request: Request, exc: ValidationException
) -> JSONResponse:
    response = JSONResponse(
        {"detail": exc.detail}, status_code=exc.status_code
    )
    if exc.headers is not None:
        response.init_headers(exc.headers)

    return response
