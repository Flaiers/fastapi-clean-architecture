from internal.utils.responses import SucessfulResponse as Response

from fastapi.types import DecoratedCallable
from fastapi_pagination import Page
from fastapi import APIRouter
from starlette.status import *

from pydantic import BaseModel

from inspect import isfunction

from typing import List


__all__ = ["APIRoutes"]


class APIRoutes:

    def __init__(self, name, router, schema) -> None:
        self.name: str = name
        self.router: APIRouter = router
        self.schema: BaseModel = schema

        self.delete_responses = Response.get_response(HTTP_200_OK)
        self.create_responses = Response.get_response(HTTP_201_CREATED)

    @classmethod
    @property
    def all(cls) -> List[str]:
        return [key for key, value in cls.__dict__.items()
                if not (key.startswith('__') and key.endswith('__'))
                and isfunction(value)]

    def list(self, func: DecoratedCallable) -> DecoratedCallable:
        self.router.add_api_route("", func, methods=["GET"],
                                  name=f"Read {self.name}s",
                                  response_model=Page[self.schema])
        return func

    def filter(self, func: DecoratedCallable) -> DecoratedCallable:
        self.router.add_api_route("/filter", func, methods=["GET"],
                                  name=f"Filter {self.name}",
                                  response_model=Page)
        return func

    def retrieve(self, func: DecoratedCallable) -> DecoratedCallable:
        self.router.add_api_route("/{id}", func, methods=["GET"],
                                  name=f"Read {self.name}",
                                  response_model=self.schema)
        return func

    def create(self, func: DecoratedCallable) -> DecoratedCallable:
        self.router.add_api_route("", func, methods=["POST"],
                                  name=f"Create {self.name}",
                                  status_code=HTTP_201_CREATED,
                                  responses=self.create_responses)
        return func

    def delete(self, func: DecoratedCallable) -> DecoratedCallable:
        self.router.add_api_route("/{id}", func, methods=["DELETE"],
                                  name=f"Delete {self.name}",
                                  responses=self.delete_responses)
        return func

    def update(self, func: DecoratedCallable) -> DecoratedCallable:
        self.router.add_api_route("/{id}", func, methods=["PUT"],
                                  name=f"Update {self.name}",
                                  response_model=self.schema)
        return func

    def partial_update(self, func: DecoratedCallable) -> DecoratedCallable:
        self.router.add_api_route("/{id}", func, methods=["PATCH"],
                                  name=f"Partial update {self.name}",
                                  response_model=self.schema)
        return func
