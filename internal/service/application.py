from internal.dto.application import BaseApplication
from internal.entity.application import Application
from internal.config.database import get_session

from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import Depends


__all__ = ["ApplicationService"]


class ApplicationService:

    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.session = session

    async def create(self, schema: BaseApplication):
        instance = Application(**schema.dict())
        self.session.add(instance)
        await self.session.commit()
        return instance
