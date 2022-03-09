from fastapi import Depends, HTTPException, APIRouter
from fastapi_pagination import paginate, Params, Page
from fastapi.types import DecoratedCallable
from starlette.status import *

from internal.app.database import get_session, Base
from .responses import SucessfulResponse
from .utils import OrderDirection

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import sqlalchemy

from typing import Any, List, Callable

from pydantic import BaseModel

from inspect import isfunction

from enum import Enum


__all__ = ["ViewSetMetaClass"]


class BaseConfig:

    include: set = set()
    exclude: set = set()
    filter_schema: BaseModel = BaseModel
    update_schema: BaseModel = BaseModel
    create_schema: BaseModel = BaseModel


class APIMethods:

    model: Base = Base
    fields: Enum = Enum("fields",
                        {"id": "id"},
                        type=str)
    filter_schema: BaseModel = BaseModel
    create_schema: BaseModel = BaseModel
    update_schema: BaseModel = BaseModel

    def __init__(
        self, query, model,
        fields, filter_schema,
        create_schema, update_schema
    ) -> None:
        self.query = query
        self.model = model
        self.fields = fields
        self.filter_schema = filter_schema
        self.create_schema = create_schema
        self.update_schema = update_schema

    @classmethod
    @property
    def all(cls) -> List[str]:
        return [key for key, value in cls.__dict__.items()
                if not (key.startswith('__') and key.endswith('__'))
                and isfunction(value)]

    async def list(
        self,
        params: Params = Depends(),
        order_by: fields = fields.id,
        db: AsyncSession = Depends(get_session),
        filter_query: filter_schema = Depends(),
        order_direction: OrderDirection = OrderDirection.asc
    ) -> Any:
        kwargs = filter_query.dict(exclude_unset=True,
                                   exclude_none=True)
        direction = getattr(sqlalchemy, order_direction)
        order_by = direction(getattr(self.model, order_by))
        instance_set = await db.execute(
            self.query.filter_by(**kwargs).order_by(order_by))

        return paginate(instance_set.scalars().all(), params)

    async def filter(
        self,
        select_by: fields,
        filter_by: str = "",
        params: Params = Depends(),
        db: AsyncSession = Depends(get_session)
    ) -> Any:
        if not hasattr(self.model, select_by):
            raise HTTPException(
                detail="Field does not exist",
                status_code=HTTP_404_NOT_FOUND
            )

        field = getattr(self.model, select_by)
        instance_set = await db.execute(
            select(field).filter(field.like(f"%{filter_by}%")))

        response = set(instance_set.scalars().all())

        return paginate(tuple(response), params)

    async def retrieve(
        self,
        id: int,
        db: AsyncSession = Depends(get_session)
    ) -> model:
        instance = await db.execute(self.query.where(self.model.id == id))
        instance = instance.scalar()
        if not instance:
            raise HTTPException(
                detail="Instance not found",
                status_code=HTTP_404_NOT_FOUND
            )
        return instance

    async def create(
        self,
        instance: create_schema,
        db: AsyncSession = Depends(get_session)
    ) -> SucessfulResponse:
        instance = self.model(**instance.dict())
        db.add(instance)
        await db.commit()
        return SucessfulResponse(HTTP_201_CREATED)

    async def delete(
        self,
        id: int,
        db: AsyncSession = Depends(get_session)
    ) -> SucessfulResponse:
        instance = await db.get(self.model, id)
        if not instance:
            raise HTTPException(
                detail="Instance not found",
                status_code=HTTP_404_NOT_FOUND
            )

        await db.delete(instance)
        await db.commit()

        return SucessfulResponse()

    async def update(
        self,
        id: int,
        instance_update: update_schema,
        db: AsyncSession = Depends(get_session)
    ) -> model:
        instance = await db.execute(self.query.where(self.model.id == id))
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

    async def partial_update(
        self,
        id: int,
        instance_update: update_schema,
        db: AsyncSession = Depends(get_session)
    ) -> model:
        instance = await db.execute(self.query.where(self.model.id == id))
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

    def __init__(self, name, router, schema) -> None:
        self.name: str = name
        self.router: APIRouter = router
        self.schema: BaseModel = schema

    def list(self) -> Callable[[DecoratedCallable], DecoratedCallable]:
        return self.router.get("", name=f"Read {self.name}s",
                               response_model=Page[self.schema])

    def filter(self) -> Callable[[DecoratedCallable], DecoratedCallable]:
        return self.router.get("/filter", name=f"Filter {self.name}",
                               response_model=Page)

    def retrieve(self) -> Callable[[DecoratedCallable], DecoratedCallable]:
        return self.router.get("/{id}", name=f"Read {self.name}",
                               response_model=self.schema)

    def create(self) -> Callable[[DecoratedCallable], DecoratedCallable]:
        return self.router.post("", name=f"Create {self.name}",
                                status_code=HTTP_201_CREATED)

    def delete(self) -> Callable[[DecoratedCallable], DecoratedCallable]:
        return self.router.delete("/{id}", name=f"Delete {self.name}")

    def update(self) -> Callable[[DecoratedCallable], DecoratedCallable]:
        return self.router.put("/{id}", name=f"Update {self.name}",
                               response_model=self.schema)

    def partial_update(self) -> Callable[[DecoratedCallable], DecoratedCallable]:
        return self.router.patch("/{id}", name=f"Partial update {self.name}",
                                 response_model=self.schema)


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
        all_methods = APIMethods.all[:]

        for include_method in include:
            if include_method not in all_methods:
                raise ValueError(f"{include_method=} does not exist")
            methods.append(include_method)

        for exclude_method in exclude:
            if exclude_method not in all_methods:
                raise ValueError(f"{exclude_method=} does not exist")
            methods.remove(exclude_method)

        for schema_type in ("create_schema", "update_schema"):
            setattr(cls, schema_type, getattr(Config, schema_type, cls.schema))

        setattr(cls, "filter_schema", getattr(Config, "filter_schema", BaseModel))
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


def method_generator(cls, method):
    name = cls.model.__name__
    router: APIRouter = cls.router

    if method == "list":
        @router.get("", name=f"Read {name}s",
                    response_model=Page[cls.schema])
        async def list(
            params: Params = Depends(),
            order_by: cls.fields = cls.fields.id,
            db: AsyncSession = Depends(get_session),
            filter_query: cls.filter_schema = Depends(),
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
        @router.get("/filter", name=f"Filter {name}",
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
        @router.get("/{id}", name=f"Read {name}",
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
        @router.post("", name=f"Create {name}",
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
        @router.delete("/{id}", name=f"Delete {name}")
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
        @router.put("/{id}", name=f"Update {name}",
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
        @router.patch("/{id}", name=f"Partial update {name}",
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
