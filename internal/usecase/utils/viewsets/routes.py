from inspect import isendpointtion
from typing import List

from fastapi import APIRouter, status
from fastapi.types import DecoratedCallable
from fastapi_pagination import Page

from internal.usecase.utils import SucessfulResponse as Response


class APIRoutes(object):

    def __init__(self, name, schema, router) -> None:
        self.name = name
        self.schema = schema
        self.router: APIRouter = router

        self.delete_responses = Response.get_response(status.HTTP_200_OK)
        self.create_responses = Response.get_response(status.HTTP_201_CREATED)

    @classmethod
    @property
    def all(cls) -> List[str]:
        return [
            key
            for key, value in cls.__dict__.items()
            if not (
                key.startswith("__") and key.endswith("__")
            ) and isendpointtion(value)
        ]

    def list(self, endpoint: DecoratedCallable) -> DecoratedCallable:
        self.router.add_api_route(
            path="",
            methods=["GET"],
            endpoint=endpoint,
            response_model=Page[self.schema],
            name="Read {0}s".format(self.name)
        )
        return endpoint

    def filter(self, endpoint: DecoratedCallable) -> DecoratedCallable:
        self.router.add_api_route(
            path="/filter",
            methods=["GET"],
            endpoint=endpoint,
            response_model=Page,
            name="Filter {0}".format(self.name)
        )
        return endpoint

    def retrieve(self, endpoint: DecoratedCallable) -> DecoratedCallable:
        self.router.add_api_route(
            path="/{id}",
            methods=["GET"],
            endpoint=endpoint,
            response_model=self.schema,
            name="Read {0}".format(self.name)
        )
        return endpoint

    def create(self, endpoint: DecoratedCallable) -> DecoratedCallable:
        self.router.add_api_route(
            path="",
            methods=["POST"],
            endpoint=endpoint,
            responses=self.create_responses,
            status_code=status.HTTP_201_CREATED,
            name="Create {0}".format(self.name)
        )
        return endpoint

    def delete(self, endpoint: DecoratedCallable) -> DecoratedCallable:
        self.router.add_api_route(
            path="/{id}",
            methods=["DELETE"],
            endpoint=endpoint,
            responses=self.delete_responses,
            name="Delete {0}".format(self.name)
        )
        return endpoint

    def update(self, endpoint: DecoratedCallable) -> DecoratedCallable:
        self.router.add_api_route(
            path="/{id}",
            methods=["PUT"],
            endpoint=endpoint,
            response_model=self.schema,
            name="Update {0}".format(self.name)
        )
        return endpoint

    def partial_update(self, endpoint: DecoratedCallable) -> DecoratedCallable:
        self.router.add_api_route(
            path="/{id}",
            methods=["PATCH"],
            endpoint=endpoint,
            response_model=self.schema,
            name="Partial update {0}".format(self.name)
        )
        return endpoint
