from fastapi import Depends

from internal.dto.application import BaseApplication
from internal.entity.application import Application
from internal.usecase.repository import Inject, Repository


class ApplicationService(object):

    def __init__(
        self,
        application_repository: Repository = Depends(Inject(Application)),
    ) -> None:
        self.application_repository = application_repository

    async def create(self, dto: BaseApplication) -> Application:
        application = self.application_repository.create(dto)
        await self.application_repository.save(application)
        return application
