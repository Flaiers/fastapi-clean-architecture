from internal.usecase.repo.application import ApplicationRepository
from internal.dto.application import BaseApplication
from internal.entity.application import Application

from fastapi import Depends


__all__ = ["ApplicationService"]


class ApplicationService:

    def __init__(
        self,
        applicationRepository: ApplicationRepository = Depends()
    ) -> None:
        self.applicationRepository = applicationRepository

    async def create(self, dto: BaseApplication) -> Application:
        application = self.applicationRepository.create(dto)
        await self.applicationRepository.save(application)
        return application
