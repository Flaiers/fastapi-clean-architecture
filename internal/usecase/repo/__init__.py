from internal.config.database import get_session, Base

from sqlalchemy.ext.asyncio import AsyncSession

from pydantic import BaseModel

from fastapi import Depends


__all__ = ["BaseRepository"]


class BaseRepository:

    model: Base = Base

    def __init__(
        self,
        session: AsyncSession = Depends(get_session)
    ) -> None:
        self.session = session

    def create(self, dto: BaseModel) -> model:
        return self.model(**dto.dict())

    async def save(self, instance: Base) -> None:
        self.session.add(instance)
        return await self.session.commit()
