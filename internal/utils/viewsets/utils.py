from internal.utils.responses import SucessfulResponse as Response
from internal.utils.enums import OrderDirection
from internal.app.database import get_session
from .routes import APIRoutes

from fastapi_pagination import paginate, Params
from fastapi import Depends, HTTPException
from starlette.status import *

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import sqlalchemy

from typing import Any


__all__ = ["method_generator"]


def method_generator(cls, method):
    name = cls.model.__name__
    routes = APIRoutes(name, cls.router, cls.schema)
    route = getattr(routes, method)

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

    async def retrieve(
        id: int,
        db: AsyncSession = Depends(get_session)
    ) -> cls.model:
        instance = await db.execute(cls.query.where(cls.model.id == id))
        instance = instance.scalar()
        if not instance:
            raise HTTPException(
                detail="Instance not found",
                status_code=HTTP_404_NOT_FOUND
            )
        return instance

    async def create(
        instance: cls.create_schema,
        db: AsyncSession = Depends(get_session)
    ) -> Response:
        instance = cls.model(**instance.dict())
        db.add(instance)
        await db.commit()
        return Response(HTTP_201_CREATED)

    async def delete(
        id: int,
        db: AsyncSession = Depends(get_session)
    ) -> Response:
        instance = await db.get(cls.model, id)
        if not instance:
            raise HTTPException(
                detail="Instance not found",
                status_code=HTTP_404_NOT_FOUND
            )

        await db.delete(instance)
        await db.commit()

        return Response()

    async def update(
        id: int,
        instance_update: cls.update_schema,
        db: AsyncSession = Depends(get_session)
    ) -> cls.model:
        instance = await db.execute(cls.query.where(cls.model.id == id))
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
        id: int,
        instance_update: cls.update_schema,
        db: AsyncSession = Depends(get_session)
    ) -> cls.model:
        instance = await db.execute(cls.query.where(cls.model.id == id))
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

    return route(locals().get(method))
