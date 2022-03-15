from fastapi import Depends

from internal.dto.application import BaseApplication
from internal.entity.application import Application
from internal.usecase.repo import InjectRepository


@InjectRepository(Application)
class ApplicationRepository(object):
    ...  # noqa: WPS604


class ApplicationService(object):

    def __init__(
        self,
        application_repository: ApplicationRepository = Depends(),
    ) -> None:
        self.application_repository = application_repository

    async def create(self, dto: BaseApplication) -> Application:
        application = self.application_repository.create(dto)
        await self.application_repository.save(application)
        return application
