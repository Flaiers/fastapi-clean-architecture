from fastapi_pagination.api import add_pagination
from fastapi import FastAPI as StandartFastAPI

from typing import Callable, Any


__all__ = ["FastAPI"]


class FastAPI(StandartFastAPI):

    def add_pagination(self):
        return add_pagination(self)

    def override_dependency(
        self,
        dependency: Callable[..., Any],
        factory: Callable[..., Any]
    ):
        self.dependency_overrides[dependency] = factory
        return self
