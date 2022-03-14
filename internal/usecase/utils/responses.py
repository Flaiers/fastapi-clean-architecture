from fastapi.responses import JSONResponse
from fastapi import status


__all__ = ["SucessfulResponse"]


class SucessfulResponse(JSONResponse):

    def __init__(
        self, status_code=None, *args, **kwargs
    ) -> None:
        kwargs |= {
            "content": {"sucessful": True},
            "status_code": status_code or status.HTTP_200_OK
        }
        super().__init__(*args, **kwargs)

    @classmethod
    def get_response(cls, status_code):
        response = {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "example": {"sucessful": True},
                }
            }
        }
        return {status_code: response}
