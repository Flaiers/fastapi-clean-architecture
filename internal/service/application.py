from internal.usecase.repo.application import ApplicationRepository
from internal.dto.application import BaseApplication
from internal.entity.application import Application

from fastapi import Depends


__all__ = ["ApplicationService"]


class ApplicationService:

    def __init__(
        self,
        application_repository: ApplicationRepository = Depends()
    ) -> None:
        self.application_repository = application_repository

    async def create(self, dto: BaseApplication) -> Application:
        application = self.application_repository.create(dto)
        await self.application_repository.save(application)
        return application
