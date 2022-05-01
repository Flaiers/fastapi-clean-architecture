from typing import Any, Callable, Generic, Type, TypeVar

import sqlalchemy as sa
from fastapi import Depends, params
from sqlalchemy import orm
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import declarative_base

from package.sqlalchemy import get_session

Base = declarative_base()
Model = TypeVar('Model', bound=Base)


class Repository(Generic[Model]):

    model: Type[Model]

    def __init__(
        self, session: AsyncSession = Depends(get_session),
    ) -> None:
        self.session = session
        self.pk_fields = (
            field.name
            for field in self.model.__mapper__.primary_key
            if field.server_default is not None
        )

    def create(self, **fields) -> Model:
        return self.model(**fields)

    async def find(self, *options, **fields) -> Result:
        statement = sa.select(self.model).filter_by(**fields).options(
            *(orm.joinedload(option) for option in options),
        )
        return await self.session.execute(statement)

    async def delete(self, instance: Model) -> None:
        await self.session.delete(instance)
        await self.session.commit()

    async def save(self, instance: Model) -> Model:
        exist = (
            field
            for field in self.pk_fields
            if getattr(instance, field) is not None
        )
        if tuple(exist):
            instance = await self.session.merge(instance)
        else:
            self.session.add(instance)

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
