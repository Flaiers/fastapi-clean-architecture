from fastapi import Depends, HTTPException, APIRouter
from fastapi_pagination import paginate, Params, Page
from starlette.status import *

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import sqlalchemy

from internal.app.database import get_session
from .responses import SucessfulResponse
from .utils import OrderDirection

from pydantic import BaseModel

from typing import Any, List, Dict

import enum


__all__ = ["ViewSetMetaClass"]
this_locals: Dict[str, Any] = dict()
APIMethods: List[str] = ["list", "filter",
                         "retrieve", "create",
                         "delete", "update",
                         "partial_update"]


class ViewSetMetaClass(type):

    def __new__(cls, *args):
        cls = super().__new__(cls, *args)

        if not (hasattr(cls, "model") or hasattr(cls, "schema")):
            raise AttributeError("Override model and schema")

        methods = APIMethods[:]
        if hasattr(cls, "Config"):
            if hasattr(cls.Config, "exclude") and \
                    hasattr(cls.Config, "include"):
                raise AttributeError("Cannot be exclude and include together")

            if hasattr(cls.Config, "exclude"):
                for method in cls.Config.exclude:
                    methods.remove(method)

            elif hasattr(cls.Config, "include"):
                include_methods = list()
                for method in cls.Config.include:
                    if method in APIMethods:
                        include_methods.append(method)
                methods = include_methods

        for schema_type in ("create_schema", "update_schema"):
            schema = getattr(getattr(cls, "Config", cls),
                             schema_type, cls.schema)
            setattr(cls, schema_type, schema)

        filter_model = getattr(cls, "filter_model", BaseModel)

        setattr(cls, "query", getattr(cls, "query", select(cls.model)))
        setattr(cls, "router", getattr(cls, "router", APIRouter()))
        setattr(cls, "filter_model", filter_model)
        setattr(cls, "fields", object)
        cls.fields = enum.Enum(
            cls.model.__name__,
            {field: field for field in cls.schema.__fields__.keys()},
            type=str
        )

        for method in methods:
            setattr(cls, method, method_generator(cls, method))

        return cls

    @classmethod
    @property
    def router(cls):
        return cls.router


def method_generator(cls, method):
    name = cls.model.__name__

    if method == "list":
        @cls.router.get("", name=f"Read {name}s",
                        response_model=Page[cls.schema])
        async def list(
            params: Params = Depends(),
            order_by: cls.fields = cls.fields.id,
            db: AsyncSession = Depends(get_session),
            filter_query: cls.filter_model = Depends(),
            order_direction: OrderDirection = OrderDirection.asc
        ) -> Any:
            kwargs = filter_query.dict(exclude_unset=True,
                                       exclude_none=True)
            direction = getattr(sqlalchemy, order_direction)
            order_by = direction(getattr(cls.model, order_by))
            instance_set = await db.execute(
                cls.query.filter_by(**kwargs).order_by(order_by))

            return paginate(instance_set.scalars().all(), params)

    elif method == "filter":
        @cls.router.get("/filter", name=f"Filter {name}",
                        response_model=Page)
        async def filter(
            select_by: cls.fields,
            filter_by: str = "",
            params: Params = Depends(),
            db: AsyncSession = Depends(get_session)
        ) -> Any:
            if not hasattr(cls.model, select_by):
                raise HTTPException(
                    detail="Field does not exist",
                    status_code=HTTP_404_NOT_FOUND
                )

            field = getattr(cls.model, select_by)
            instance_set = await db.execute(
                select(field).filter(field.like(f"%{filter_by}%")))

            response = set(instance_set.scalars().all())

            return paginate(tuple(response), params)

    elif method == "retrieve":
        @cls.router.get("/{id}", name=f"Read {name}",
                        response_model=cls.schema)
        async def retrieve(
            id: int,
            db: AsyncSession = Depends(get_session)
        ) -> cls.model:
            instance = await db.execute(
                cls.query.where(cls.model.id == id))
            instance = instance.scalar()
            if not instance:
                raise HTTPException(
                    detail="Instance not found",
                    status_code=HTTP_404_NOT_FOUND
                )
            return instance

    elif method == "create":
        @cls.router.post("", name=f"Create {name}",
                         status_code=HTTP_201_CREATED)
        async def create(
            instance: cls.create_schema,
            db: AsyncSession = Depends(get_session)
        ) -> SucessfulResponse:
            instance = cls.model(**instance.dict())
            db.add(instance)
            await db.commit()
            return SucessfulResponse(HTTP_201_CREATED)

    elif method == "delete":
        @cls.router.delete("/{id}", name=f"Delete {name}")
        async def delete(
            id: int,
            db: AsyncSession = Depends(get_session)
        ) -> SucessfulResponse:
            instance = await db.get(cls.model, id)
            if not instance:
                raise HTTPException(
                    detail="Instance not found",
                    status_code=HTTP_404_NOT_FOUND
                )

            await db.delete(instance)
            await db.commit()

            return SucessfulResponse()

    elif method == "update":
        @cls.router.put("/{id}", name=f"Update {name}",
                        response_model=cls.schema)
        async def update(
            id: int,
            instance_update: cls.update_schema,
            db: AsyncSession = Depends(get_session)
        ) -> cls.model:
            instance = await db.execute(
                cls.query.where(cls.model.id == id))
            instance = instance.scalar()
            if not instance:
                raise HTTPException(
                    detail="Instance not found",
                    status_code=HTTP_404_NOT_FOUND
                )

            for key, value in instance_update.dict().items():
                setattr(instance, key, value)

            db.add(instance)
            await db.commit()
            await db.refresh(instance)

            return instance

    elif method == "partial_update":
        @cls.router.patch("/{id}", name=f"Partial update {name}",
                          response_model=cls.schema)
        async def partial_update(
            id: int,
            instance_update: cls.update_schema,
            db: AsyncSession = Depends(get_session)
        ) -> cls.model:
            instance = await db.execute(
                cls.query.where(cls.model.id == id))
            instance = instance.scalar()
            if not instance:
                raise HTTPException(
                    detail="Instance not found",
                    status_code=HTTP_404_NOT_FOUND
                )

            items = instance_update.dict(
                exclude_unset=True, exclude_none=True).items()
            for key, value in items:
                setattr(instance, key, value)

            db.add(instance)
            await db.commit()
            await db.refresh(instance)

            return instance

    if not this_locals:
        this_locals |= locals()

    return this_locals.get(method)
