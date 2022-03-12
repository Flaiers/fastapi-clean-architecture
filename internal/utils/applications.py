from fastapi_pagination.api import add_pagination
from fastapi import FastAPI as StandartFastAPI


__all__ = ["FastAPI"]


class FastAPI(StandartFastAPI):

    def add_pagination(self):
        return add_pagination(self)
