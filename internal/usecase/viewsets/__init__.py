from .utils import method_generator
from .config import BaseConfig
from .routes import APIRoutes

from pydantic import BaseModel

from fastapi import APIRouter

from sqlalchemy import select

from enum import Enum


__all__ = ["ViewSetMetaClass"]


class ViewSetMetaClass(type):

    def __new__(cls, *args):
        cls = super().__new__(cls, *args)
        Config = getattr(cls, "Config", BaseConfig)
        include = getattr(Config, "include", set())
        exclude = getattr(Config, "exclude", set())

        if not (hasattr(cls, "model") or hasattr(cls, "schema")):
            raise AttributeError("Override model and schema")

        if include and exclude:
            raise AttributeError("Cannot be exclude and include together")

        methods = list()
        all_methods = APIRoutes.all[:]

        for include_method in include:
            if include_method not in all_methods:
                raise ValueError(f"{include_method=} does not exist")
            methods.append(include_method)

        for exclude_method in exclude:
            if exclude_method not in all_methods:
                raise ValueError(f"{exclude_method=} does not exist")
            all_methods.remove(exclude_method)

        for schema_type in ("create_schema", "update_schema"):
            setattr(cls, schema_type, getattr(Config, schema_type, cls.schema))

        setattr(cls, "filter_schema", getattr(Config, "filter_schema", BaseModel()))
        setattr(cls, "query", getattr(cls, "query", select(cls.model)))
        setattr(cls, "router", getattr(cls, "router", APIRouter()))
        setattr(cls, "fields", object)
        cls.fields = Enum(
            cls.model.__name__,
            {field: field for field in cls.schema.__fields__.keys()},
            type=str
        )

        if not methods:
            methods = all_methods

        for method in methods:
            setattr(cls, method, method_generator(cls, method))

        return cls