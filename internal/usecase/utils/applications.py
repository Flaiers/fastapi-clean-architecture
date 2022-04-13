from typing import Any, Callable

from fastapi import FastAPI as MainFastAPI
from fastapi_pagination.api import add_pagination


class FastAPI(MainFastAPI):

    def __init__(self, *, settings):
        super().__init__(
            title=settings.PROJECT_NAME,
            description=settings.DESCRIPTION,
            version=settings.VERSION,
            openapi_url='{0}/openapi.json'.format(settings.DOCS),
            swagger_ui_parameters=settings.SWAGGER_UI_PARAMETERS,
        )

    def add_pagination(self):
        return add_pagination(self)

    def override_dependency(
        self,
        dependency: Callable[..., Any],
        factory: Callable[..., Any],
    ):
        self.dependency_overrides[dependency] = factory
        return self
