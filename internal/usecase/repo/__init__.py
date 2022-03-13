from sqlalchemy.ext.asyncio import AsyncSession

from internal.entity import Base
from ..utils import get_session

from pydantic import BaseModel

from fastapi import Depends


__all__ = ["BaseRepository"]


class BaseRepository:

    model: Base = Base

    def __init__(
        self, session: AsyncSession = Depends(get_session)
    ) -> None:
        self.session = session

    def create(self, dto: BaseModel, **kwargs) -> model:
        return self.model(**dto.dict(**kwargs))

    async def save(self, instance: model) -> None:
        self.session.add(instance)
        return await self.session.commit()