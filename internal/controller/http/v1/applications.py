import uuid
from typing import Any

from fastapi import APIRouter, Depends, status
from fastapi_pagination import Page, Params, paginate

from internal.dto.application import (
    ApplicationFilter,
    ApplicationRead,
    BaseApplication,
)
from internal.service.application import ApplicationService
from internal.usecase.utils import SuccessfulResponse, response

router = APIRouter()


@router.get('', response_model=Page[ApplicationRead])
async def read_applications(
    dto: ApplicationFilter = Depends(),
    pagination_params: Params = Depends(),
    application_service: ApplicationService = Depends(),
) -> Any:
    applications = await application_service.find(dto)
    return paginate(applications, pagination_params)


@router.post(
    path='',
    response_model=ApplicationRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_application(
    dto: BaseApplication,
    application_service: ApplicationService = Depends(),
) -> ApplicationRead:
    return await application_service.create(dto)


@router.delete(
    path='/{application_id}',
    responses=response.HTTP_404_NOT_FOUND(
        'Application not found',
    ) | SuccessfulResponse.schema(),
)
async def delete_application(
    application_id: uuid.UUID,
    application_service: ApplicationService = Depends(),
) -> SuccessfulResponse:
    await application_service.delete(application_id)
    return SuccessfulResponse()
