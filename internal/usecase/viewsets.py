from fastapi import Depends, HTTPException, APIRouter
from fastapi_pagination import paginate, Params, Page
from starlette.status import *

from internal.app.database import get_session, Base
from .responses import SucessfulResponse
from .utils import OrderDirection

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import sqlalchemy

from pydantic import BaseModel

from typing import Any

import enum


__all__ = ["ViewSetMetaClass"]


class APIMethods:

    query: Any
    model: Base
    fields: enum.Enum
    filter_schema: BaseModel
    create_schema: BaseModel
    update_schema: BaseModel

    def __new__(
        cls, query, model, fields,
        filter_schema, create_schema,
        update_schema, *args
    ):
        cls = super().__new__(cls, *args)
        cls.query = query
        cls.model = model
        cls.fields = fields
        cls.filter_schema = filter_schema
        cls.create_schema = create_schema
        cls.update_schema = update_schema
        return cls

    @classmethod
    @property
    def _all(cls):
        return tuple(filter(lambda k: not k.startswith("_"), dir(cls)))

    @staticmethod
    async def list(
        params: Params = Depends(),
        order_by: fields = fields.id,
        db: AsyncSession = Depends(get_session),
        filter_query: filter_schema = Depends(),
        order_direction: OrderDirection = OrderDirection.asc
    ) -> Any:
        kwargs = filter_query.dict(exclude_unset=True,
                                   exclude_none=True)
        direction = getattr(sqlalchemy, order_direction)
        order_by = direction(getattr(model, order_by))
        instance_set = await db.execute(
            query.filter_by(**kwargs).order_by(order_by))

        return paginate(instance_set.scalars().all(), params)

    @staticmethod
    async def filter(
        select_by: fields,
        filter_by: str = "",
        params: Params = Depends(),
        db: AsyncSession = Depends(get_session)
    ) -> Any:
        if not hasattr(model, select_by):
            raise HTTPException(
                detail="Field does not exist",
                status_code=HTTP_404_NOT_FOUND
            )

        field = getattr(model, select_by)
        instance_set = await db.execute(
            select(field).filter(field.like(f"%{filter_by}%")))

        response = set(instance_set.scalars().all())

        return paginate(tuple(response), params)

    @staticmethod
    async def retrieve(
        id: int,
        db: AsyncSession = Depends(get_session)
    ) -> model:
        instance = await db.execute(query.where(model.id == id))
        instance = instance.scalar()
        if not instance:
            raise HTTPException(
                detail="Instance not found",
                status_code=HTTP_404_NOT_FOUND
            )
        return instance

    @staticmethod
    async def create(
        instance: create_schema,
        db: AsyncSession = Depends(get_session)
    ) -> SucessfulResponse:
        instance = model(**instance.dict())
        db.add(instance)
        await db.commit()
        return SucessfulResponse(HTTP_201_CREATED)

    @staticmethod
    async def delete(
        id: int,
        db: AsyncSession = Depends(get_session)
    ) -> SucessfulResponse:
        instance = await db.get(model, id)
        if not instance:
            raise HTTPException(
                detail="Instance not found",
                status_code=HTTP_404_NOT_FOUND
            )

        await db.delete(instance)
        await db.commit()

        return SucessfulResponse()

    @staticmethod
    async def update(
        id: int,
        instance_update: update_schema,
        db: AsyncSession = Depends(get_session)
    ) -> model:
        instance = await db.execute(query.where(model.id == id))
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

    @staticmethod
    async def partial_update(
        id: int,
        instance_update: update_schema,
        db: AsyncSession = Depends(get_session)
    ) -> model:
        instance = await db.execute(query.where(model.id == id))
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


class APIDecorators:

    def __init__(self, name, router, schema):
        self.name: str = name
        self.router: APIRouter = router
        self.schema: BaseModel = schema

    def list(self):
        return self.router.get("", name=f"Read {self.name}s",
                               response_model=Page[self.schema])

    def filter(self):
        return self.router.get("/filter", name=f"Filter {self.name}",
                               response_model=Page)

    def retrieve(self):
        return self.router.get("/{id}", name=f"Read {self.name}",
                               response_model=self.schema)

    def create(self):
        return self.router.post("", name=f"Create {self.name}",
                                status_code=HTTP_201_CREATED)

    def delete(self):
        return self.router.delete("/{id}", name=f"Delete {self.name}")

    def update(self):
        return self.router.put("/{id}", name=f"Update {self.name}",
                               response_model=self.schema)

    def partial_update(self):
        return self.router.patch("/{id}", name=f"Partial update {self.name}",
                                 response_model=self.schema)


class ViewSetMetaClass(type):

    def __new__(cls, *args):
        cls = super().__new__(cls, *args)

        if not (hasattr(cls, "model") or hasattr(cls, "schema")):
            raise AttributeError("Override model and schema")

        methods = set(APIMethods._all)
        if hasattr(cls, "Config"):
            if hasattr(cls.Config, "exclude") and \
                    hasattr(cls.Config, "include"):
                raise AttributeError("Cannot be exclude and include together")

            if hasattr(cls.Config, "exclude"):
                for method in cls.Config.exclude:
                    methods.remove(method)

            elif hasattr(cls.Config, "include"):
                include_methods = set()
                for method in cls.Config.include:
                    if method in methods:
                        include_methods.add(method)
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

    return locals().get(method)
