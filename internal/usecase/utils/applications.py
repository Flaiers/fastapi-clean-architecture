from typing import Any, Callable

from fastapi import FastAPI as MainFastAPI
from fastapi_pagination.api import add_pagination

__all__ = "FastAPI"


class FastAPI(MainFastAPI):

    def add_pagination(self):
        return add_pagination(self)

    def override_dependency(
        self,
        dependency: Callable[..., Any],
        factory: Callable[..., Any]
    ):
        self.dependency_overrides[dependency] = factory
        return self
