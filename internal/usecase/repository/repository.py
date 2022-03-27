from typing import Any, Callable, Generic, Type, TypeVar

from fastapi import Depends, params
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from internal.entity.base import Base
from internal.usecase.utils import get_session

Model = TypeVar('Model', bound=Base)
Dto = TypeVar('Dto', bound=BaseModel)


class Repository(Generic[Model]):

    model: Type[Model]

    def __init__(
        self, session: AsyncSession = Depends(get_session)
    ) -> None:
        self.session = session

    def create(self, dto: Type[Dto], **kwargs) -> Type[Model]:
        return self.model(**dto.dict(**kwargs))

    async def save(self, instance: Type[Model]) -> None:
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
