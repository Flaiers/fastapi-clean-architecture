from typing import Any, Callable, Dict, Generic, Sequence, TypeVar

import sqlalchemy as sa
from fastapi import Depends, params
from multimethod import multimethod as overload
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import (
    DeclarativeMeta,
    declarative_base,
)

from package.sqlalchemy import get_session
from package.sqlalchemy.repository import AbstractRepository

Base: DeclarativeMeta = declarative_base()
Model = TypeVar('Model', bound=Base)


class Repository(AbstractRepository, Generic[Model]):

    def __init__(
        self, session: AsyncSession = Depends(get_session),
    ) -> None:
        self.session = session
        self.primary_keys = (
            pk
            for pk in self.model.__mapper__.primary_key
            if pk.server_default is not None
        )

    @overload
    def create(self, **attrs) -> Model:
        return self.model(**attrs)

    @overload
    def create(self, attrs: Dict[str, Any]) -> Model:
        return self.model(**attrs)

    @overload
    def merge(self, instance: Model, **attrs) -> Model:
        for attr_key, attr_value in attrs.items():
            setattr(instance, attr_key, attr_value)

        return instance

    @overload
    def merge(self, instance: Model, attrs: Dict[str, Any]) -> Model:
        for attr_key, attr_value in attrs.items():
            setattr(instance, attr_key, attr_value)

        return instance

    def has_pk(self, instance: Model) -> bool:
        return bool([
            attr
            for pk in self.primary_keys
            if (attr := getattr(instance, pk.name)) is not None
        ])

    def get_pk(self, instance: Model) -> Dict[str, Any] | Any:
        primary_keys = {
            pk.name: attr
            for pk in self.primary_keys
            if (attr := getattr(instance, pk.name)) is not None
        }

        if len(primary_keys) > 1:
            return primary_keys

        return next(iter(primary_keys.values()))

    async def count(self, *where, **attrs) -> int:
        statement = sa.select(sa.func.count(
        )).select_from(self.model).where(*where).filter_by(**attrs)
        return await self.session.scalar(statement)

    async def delete(self, *where, **attrs) -> None:
        statement = sa.delete(self.model).where(*where).filter_by(**attrs)
        await self.session.execute(statement)
        await self.session.commit()

    async def find(self, *where, **attrs) -> Sequence[Model]:
        statement = sa.select(self.model).where(*where).filter_by(**attrs)
        return (await self.session.scalars(statement)).unique().all()

    async def find_one(self, *where, **attrs) -> Model | None:
        statement = sa.select(self.model).where(*where).filter_by(**attrs)
        return await self.session.scalar(statement)

    async def find_one_or_fail(self, *where, **attrs) -> Model:
        instance = await self.find_one(*where, **attrs)
        if instance is None:
            raise NoResultFound('{0.__name__} not found'.format(self.model))

        return instance

    @overload
    async def remove(self, instance: Model) -> None:
        await self.session.delete(instance)
        await self.session.commit()

    @overload
    async def remove(self, instances: Sequence[Model]) -> None:
        for instance in instances:
            await self.session.delete(instance)

        await self.session.commit()

    @overload
    async def pre_save(self, instance: Model) -> Model:
        self.session.add(instance)
        await self.session.flush()
        return instance

    @overload
    async def pre_save(self, instances: Sequence[Model]) -> Sequence[Model]:
        self.session.add_all(instances)
        await self.session.flush()
        return instances

    @overload
    async def save(self, instance: Model) -> Model:
        await self.pre_save(instance)
        await self.session.commit()
        return instance

    @overload
    async def save(self, instances: Sequence[Model]) -> Sequence[Model]:
        await self.pre_save(instances)
        await self.session.commit()
        return instances


def Inject(  # noqa: N802
    model: Callable[..., Any], *, use_cache: bool = True,
) -> Any:
    class_name = '{0.__name__}{1.__name__}'.format(model, Repository)
    class_bases = (Repository,)
    class_namespace = {'model': model}
    dependency = type(class_name, class_bases, class_namespace)
    return params.Depends(dependency=dependency, use_cache=use_cache)
