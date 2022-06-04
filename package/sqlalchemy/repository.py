from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    Sequence,
    Type,
    TypeVar,
)

import sqlalchemy as sa
from fastapi import Depends, params
from multimethod import multimethod as overload
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import (
    DeclarativeMeta,
    declarative_base,
)

from package.sqlalchemy import get_session

Base: DeclarativeMeta = declarative_base()
Model = TypeVar('Model', bound=Base)


class Repository(Generic[Model]):

    model: Type[Model]

    def __init__(
        self, session: AsyncSession = Depends(get_session),
    ) -> None:
        self.session = session
        self.primary_keys = (
            pk
            for pk in self.model.__mapper__.primary_key
            if pk.server_default is not None
        )

    def create(self, **attrs) -> Model:
        return self.model(**attrs)

    def merge(self, instance: Model, **attrs) -> Model:
        for attr_key, attr_value in attrs.items():
            setattr(instance, attr_key, attr_value)

        return instance

    def has_pk(self, instance: Model) -> bool:
        return bool([
            pk
            for pk in self.primary_keys
            if getattr(instance, pk.name) is not None
        ])

    def get_pk(self, instance: Model) -> Dict[str, Any] | Any:
        primary_keys = {}
        for pk in self.primary_keys:
            field = getattr(instance, pk.name)
            if field is not None:
                primary_keys[pk.name] = field

        if len(primary_keys) > 1:
            return primary_keys

        return next(iter(primary_keys.values()))

    async def find(self, *where, **attrs) -> Result:
        statement = sa.select(self.model).where(*where).filter_by(**attrs)
        return await self.session.execute(statement)

    @overload
    async def delete(self, *where, **attrs) -> None:
        statement = sa.delete(self.model).where(*where).filter_by(**attrs)
        await self.session.execute(statement)
        await self.session.commit()

    @overload
    async def delete(self, instances: Sequence[Model]) -> None:
        for instance in instances:
            await self.session.delete(instance)
        await self.session.commit()

    @overload
    async def delete(self, instance: Model) -> None:
        await self.session.delete(instance)
        await self.session.commit()

    async def pre_save(self, instance: Model) -> Model:
        self.session.add(instance)
        await self.session.flush()
        return instance

    async def save(self, instance: Model) -> Model:
        await self.pre_save(instance)
        await self.session.commit()
        return instance


def Inject(  # noqa: N802
    model: Callable[..., Any], *, use_cache: bool = True,
) -> Any:
    class_name = '{0.__name__}{1.__name__}'.format(model, Repository)
    class_bases = (Repository,)
    class_namespace = {'model': model}
    dependency = type(class_name, class_bases, class_namespace)
    return params.Depends(dependency=dependency, use_cache=use_cache)
