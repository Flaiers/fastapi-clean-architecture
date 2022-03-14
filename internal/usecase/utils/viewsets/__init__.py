from enum import Enum

from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import select

from .builder import build_method
from .config import BaseConfig
from .routes import APIRoutes


class ViewSetMetaClass(type):

    def __new__(mcs, *args, **kwargs):  # noqa: N804
        cls = super().__new__(mcs, *args, **kwargs)  # noqa: WPS117
        config = getattr(cls, "Config", BaseConfig)
        include = getattr(config, "include", set())
        exclude = getattr(config, "exclude", set())

        if not (hasattr(cls, "model") or hasattr(cls, "schema")):
            raise AttributeError("Override model and schema")

        if include and exclude:
            raise AttributeError("Cannot be exclude and include together")

        methods = []
        all_methods = APIRoutes.all[:]

        for include_method in include:
            if include_method not in all_methods:
                raise ValueError(
                    f"{include_method=} does not exist"  # noqa: WPS305
                )
            methods.append(include_method)

        for exclude_method in exclude:
            if exclude_method not in all_methods:
                raise ValueError(
                    f"{exclude_method=} does not exist"  # noqa: WPS305
                )
            all_methods.remove(exclude_method)

        for schema_type in ("create_schema", "update_schema"):
            setattr(cls, schema_type, getattr(config, schema_type, cls.schema))

        setattr(cls, "filter_schema", getattr(config, "filter_schema", BaseModel))  # noqa: E501
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
            setattr(cls, method, build_method(cls, method))

        return cls
