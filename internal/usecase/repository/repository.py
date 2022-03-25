from typing import Any, Callable, Type

from fastapi import Depends, params
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from internal.entity.base import Base
from internal.usecase.utils import get_session


class Repository(object):

    model: Type[Base] = Base

    def __init__(
        self, session: AsyncSession = Depends(get_session)
    ) -> None:
        self.session = session

    def create(self, dto: Type[BaseModel], **kwargs) -> model:
        return self.model(**dto.dict(**kwargs))

    async def save(self, instance: model) -> None:
        self.session.add(instance)
        await self.session.commit()


def Inject(  # noqa: N802
    model: Callable[..., Any], *, use_cache: bool = True
) -> Any:
    class_name = '{0.__name__}{1.__name__}'.format(model, Repository)
    class_bases = (Repository,)
    class_namespace = {'model': model}
    dependency = type(class_name, class_bases, class_namespace)
    return params.Depends(dependency=dependency, use_cache=use_cache)
