import uuid
from datetime import datetime
from typing import Sequence

from fastapi import Depends
from pytorm.repository import InjectRepository
from sqlalchemy.ext.asyncio import AsyncSession

from internal.dto.application import (
    ApplicationFilter,
    BaseApplication,
)
from internal.entity.application import Application
from internal.usecase.utils import get_session


class ApplicationService(object):

    def __init__(
        self, session: AsyncSession = Depends(get_session),
    ) -> None:
        self.repository = InjectRepository(Application, session)

    async def create(self, dto: BaseApplication) -> Application:
        application = self.repository.create(**dto.dict())
        return await self.repository.save(application)

    async def find(self, dto: ApplicationFilter) -> Sequence[Application]:
        return await self.repository.find(
            Application.phone.contains(dto.phone),
            Application.email.contains(dto.email),
        )

    async def find_one_or_fail(self, application_id: uuid.UUID) -> Application:
        return await self.repository.find_one_or_fail(id=application_id)

    async def delete(self, application_id: uuid.UUID) -> Application:
        application = await self.find_one_or_fail(application_id)
        application.deleted_at = datetime.now()
        return await self.repository.save(application)
