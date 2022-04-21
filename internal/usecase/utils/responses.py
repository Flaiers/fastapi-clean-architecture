from typing import Any, Dict

from fastapi import status
from fastapi.responses import JSONResponse


class response_schema(dict):  # noqa: WPS600, N801

    def __init__(
        self,
        example: Dict[Any, Any],
        description: str,
        status_code: int,
    ):
        self.example = example
        self.description = description
        self.status_code = status_code
        super().__init__({status_code: {
            'description': description,
            'content': {
                'application/json': {
                    'example': example,
                },
            },
        }})

    def __call__(
        self,
        example: Dict[Any, Any] = {},  # noqa: B006
        description: str = '',
    ):
        self.__init__(
            example or self.example,
            description or self.description,
            self.status_code,
        )
        return self


class SucessfulResponse(JSONResponse):

    def __init__(
        self, status_code: int = status.HTTP_200_OK, **kwargs,
    ) -> None:
        kwargs |= {
            'content': {'sucessful': True},
            'status_code': status_code,
        }
        super().__init__(**kwargs)

    @classmethod
    def schema(cls, status_code: int):
        return response_schema(
            example={'sucessful': True},
            description='Sucessful Response',
            status_code=status_code,
        )
