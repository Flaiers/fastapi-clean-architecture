import uuid

from fastapi import APIRouter, Depends, HTTPException, status

from internal.dto.application import ApplicationRead, BaseApplication
from internal.service.application import ApplicationService
from internal.usecase.utils import SuccessfulResponse, response

router = APIRouter()


@router.post(
    path='',
    response_model=ApplicationRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_application(
    dto: BaseApplication,
    application_service: ApplicationService = Depends(),
) -> SuccessfulResponse:
    return await application_service.create(dto)


@router.delete(
    path='/{application_id}',
    responses=response.RESPONSE_404_NOT_FOUND(
        'Application not found',
    ) | SuccessfulResponse.schema(),
)
async def delete_application(
    application_id: uuid.UUID,
    application_service: ApplicationService = Depends(),
) -> SuccessfulResponse:
    instance = await application_service.find_one_or_none(application_id)
    if instance is None:
        raise HTTPException(
            detail='Application not found',
            status_code=status.HTTP_404_NOT_FOUND,
        )

    await application_service.delete(instance)
    return SuccessfulResponse()
