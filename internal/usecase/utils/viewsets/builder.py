from ..responses import SucessfulResponse as Response
from ..enums import OrderDirection
from ..mocks import get_session
from .routes import APIRoutes

from fastapi import Depends, HTTPException, status
from fastapi_pagination import paginate, Params

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import sql, select

from typing import Any


__all__ = ["build_method"]


def build_method(args, method):
    name = args.model.__name__
    routes = APIRoutes(name, args.schema, args.router)
    route = getattr(routes, method)

    async def list(
        params: Params = Depends(),
        order_by: args.fields = args.fields.id,
        db: AsyncSession = Depends(get_session),
        filter_query: args.filter_schema = Depends(),
        order_direction: OrderDirection = OrderDirection.asc
    ) -> Any:
        kwargs = filter_query.dict(
            exclude_unset=True, exclude_none=True
        )
        direction = getattr(sql, order_direction)
        order_by = direction(getattr(args.model, order_by))
        instance_set = await db.execute(
            args.query.filter_by(**kwargs).order_by(order_by)
        )

        return paginate(instance_set.scalars().all(), params)

    async def filter(
        select_by: args.fields,
        filter_by: str = "",
        params: Params = Depends(),
        db: AsyncSession = Depends(get_session)
    ) -> Any:
        if not hasattr(args.model, select_by):
            raise HTTPException(
                detail="Field does not exist",
                status_code=status.HTTP_404_NOT_FOUND
            )

        field = getattr(args.model, select_by)
        instance_set = await db.execute(
            select(field).filter(field.like("%{0}%".format(filter_by)))
        )
        response = set(instance_set.scalars().all())

        return paginate(tuple(response), params)

    async def retrieve(
        id: int,
        db: AsyncSession = Depends(get_session)
    ) -> args.model:
        instance = await db.execute(args.query.where(args.model.id == id))
        instance = instance.scalar()
        if not instance:
            raise HTTPException(
                detail="Instance not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        return instance

    async def create(
        instance: args.create_schema,
        db: AsyncSession = Depends(get_session)
    ) -> Response:
        instance = args.model(**instance.dict())
        db.add(instance)
        await db.commit()
        return Response(status.HTTP_201_CREATED)

    async def delete(
        id: int,
        db: AsyncSession = Depends(get_session)
    ) -> Response:
        instance = await db.get(args.model, id)
        if not instance:
            raise HTTPException(
                detail="Instance not found",
                status_code=status.HTTP_404_NOT_FOUND
            )

        await db.delete(instance)
        await db.commit()

        return Response()

    async def update(
        id: int,
        instance_update: args.update_schema,
        db: AsyncSession = Depends(get_session)
    ) -> args.model:
        instance = await db.execute(args.query.where(args.model.id == id))
        instance = instance.scalar()
        if not instance:
            raise HTTPException(
                detail="Instance not found",
                status_code=status.HTTP_404_NOT_FOUND
            )

        for key, value in instance_update.dict().items():
            setattr(instance, key, value)

        db.add(instance)
        await db.commit()
        await db.refresh(instance)

        return instance

    async def partial_update(
        id: int,
        instance_update: args.update_schema,
        db: AsyncSession = Depends(get_session)
    ) -> args.model:
        instance = await db.execute(args.query.where(args.model.id == id))
        instance = instance.scalar()
        if not instance:
            raise HTTPException(
                detail="Instance not found",
                status_code=status.HTTP_404_NOT_FOUND
            )

        items = instance_update.dict(
            exclude_unset=True, exclude_none=True
        ).items()
        for key, value in items:
            setattr(instance, key, value)

        db.add(instance)
        await db.commit()
        await db.refresh(instance)

        return instance

    return route(locals().get(method))
