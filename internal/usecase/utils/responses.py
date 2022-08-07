from typing import Any, Dict, TypedDict

from fastapi import status
from fastapi.responses import JSONResponse
from typing_extensions import NotRequired


class ResponseExample(TypedDict):

    successful: bool
    detail: NotRequired[str]


class ResponseSchema(dict):  # noqa: WPS600

    def __init__(
        self,
        status_code: int,
        description: str,
        example: ResponseExample,
    ) -> None:
        self.example = example
        self.status_code = status_code
        self.description = description
        super().__init__(self.schema(
            example=example,
            status_code=status_code,
            description=description,
        ))

    def __call__(self, detail: str = '', description: str = ''):
        example = self.example.copy()
        example['detail'] = detail or example['detail']
        return self.schema(
            example=example,
            status_code=self.status_code,
            description=description or self.description,
        )

    @classmethod
    def schema(
        cls,
        status_code: int,
        description: str,
        example: ResponseExample,
    ) -> Dict[int, Dict[str, Any]]:
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
    def schema(cls, status_code: int = status.HTTP_200_OK) -> ResponseSchema:
        return ResponseSchema(
            status_code=status_code,
            description='Successful Response',
            example=ResponseExample(successful=True),
        )
