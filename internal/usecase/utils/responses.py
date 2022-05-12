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
        super().__init__(self.schema(example, description, status_code))

    def __call__(self, detail: str = '', description: str = ''):
        example = self.example.copy()
        example['detail'] = detail or example['detail']
        return self.schema(
            example,
            description or self.description,
            self.status_code,
        )

    def schema(
        self,
        example: Dict[Any, Any],
        description: str,
        status_code: int,
    ):
        return {
            status_code: {
                'description': description,
                'content': {
                    'application/json': {
                        'example': example,
                    },
                },
            },
        }


class SuccessfulResponse(JSONResponse):

    def __init__(
        self, status_code: int = status.HTTP_200_OK, **kwargs,
    ) -> None:
        kwargs |= {
            'content': {'successful': True},
            'status_code': status_code,
        }
        super().__init__(**kwargs)

    @classmethod
    def schema(cls, status_code: int = status.HTTP_200_OK):
        return response_schema(
            example={'successful': True},
            description='Successful Response',
            status_code=status_code,
        )
