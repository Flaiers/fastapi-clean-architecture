from starlette.responses import JSONResponse
from starlette.status import *


__all__ = ["SucessfulResponse"]


class SucessfulResponse(JSONResponse):

    def __init__(
        self,
        status_code=HTTP_200_OK,
        *args, **kwargs
    ) -> None:
        kwargs |= dict(
            status_code=status_code,
            content={"sucessful": True}
        )
        super().__init__(*args, **kwargs)
