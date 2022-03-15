from fastapi import Depends

from internal.dto.application import BaseApplication
from internal.entity.application import Application
from internal.usecase.repo import InjectRepository
from internal.usecase.utils import get_application_repository

override_repository = get_application_repository, InjectRepository(Application)


class ApplicationService(object):

    def __init__(
        self,
        application_repository=Depends(get_application_repository),
    ) -> None:
        self.application_repository = application_repository

    async def create(self, dto: BaseApplication) -> Application:
        application = self.application_repository.create(dto)
        await self.application_repository.save(application)
        return application
