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
