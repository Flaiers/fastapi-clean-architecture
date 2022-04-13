from typing import Any, Callable, Dict

from fastapi import status
from fastapi.responses import JSONResponse


def response_schema(
    content: Dict[Any, Any],  # noqa: WPS110
    status_code: int,
    description: str,
    editable: bool = False,
) -> Callable[..., Dict[int, Any]] | Dict[int, Any]:
    def wrapper(
        wrapped_content: Dict[Any, Any] = content,
        wrapped_description: str = description,
    ) -> Dict[int, Any]:
        return {status_code: {
            'description': wrapped_description,
            'content': {
                'application/json': {
                    'example': wrapped_content,
                },
            },
        }}
    return wrapper if editable else wrapper()


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
            content={'sucessful': True},
            status_code=status_code,
            description='Sucessful Response',
        )
