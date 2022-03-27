from fastapi import status
from fastapi.responses import JSONResponse


class SucessfulResponse(JSONResponse):

    def __init__(
        self, status_code: int = status.HTTP_200_OK, *args, **kwargs
    ) -> None:
        kwargs |= {
            'content': {'sucessful': True},
            'status_code': status_code
        }
        super().__init__(*args, **kwargs)

    @classmethod
    def get_response(cls, status_code: int):
        response = {
            'description': 'Successful Response',
            'content': {
                'application/json': {
                    'example': {'sucessful': True},
                }
            }
        }
        return {status_code: response}
