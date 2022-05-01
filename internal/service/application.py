import uuid

from internal.dto.application import BaseApplication
from internal.entity.application import Application
from package.sqlalchemy.repository import Inject, Repository


class ApplicationService(object):

    def __init__(
        self,
        repository: Repository[Application] = Inject(Application),
    ) -> None:
        self.repository = repository

    async def create(self, dto: BaseApplication) -> Application:
        application = self.repository.create(**dto.dict())
        return await self.repository.save(application)

    async def find_one_or_none(self, application_id: uuid.UUID) -> Application:
        query_result = await self.repository.find(id=application_id)
        return query_result.scalar_one_or_none()

    async def delete(self, application_id: uuid.UUID) -> bool | None:
        application = await self.find_one_or_none(application_id)
        if application is not None:
            await self.repository.delete(application)
            return True
