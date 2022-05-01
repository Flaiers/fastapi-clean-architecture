import uuid

from fastapi import APIRouter, Depends, HTTPException, status

from internal.dto.application import BaseApplication
from internal.service.application import ApplicationService
from internal.usecase.utils import SuccessfulResponse, response

router = APIRouter()
create_response = SuccessfulResponse.schema(status.HTTP_201_CREATED)


@router.post(
    path='',
    responses=create_response,
    status_code=status.HTTP_201_CREATED,
)
async def create_application(
    dto: BaseApplication,
    application_service: ApplicationService = Depends(),
) -> SuccessfulResponse:
    await application_service.create(dto)
    return SuccessfulResponse(status_code=status.HTTP_201_CREATED)


@router.delete(
    path='',
    responses=response.RESPONSE_404_NOT_FOUND(
        'Application not found',
    ) | SuccessfulResponse.schema(),
)
async def delete_application(
    application_id: uuid.UUID,
    application_service: ApplicationService = Depends(),
) -> SuccessfulResponse:
    deleted = await application_service.delete(application_id)
    if not deleted:
        raise HTTPException(
            detail='Application not found',
            status_code=status.HTTP_404_NOT_FOUND,
        )

    return SuccessfulResponse()
