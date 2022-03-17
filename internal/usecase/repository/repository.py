from typing import Type

from fastapi import Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from internal.entity import Base
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