from fastapi import APIRouter, Depends, status

from internal.dto.application import BaseApplication
from internal.service.application import ApplicationService
from internal.usecase.utils import SucessfulResponse as Response

router = APIRouter()
create_response = Response.schema(status.HTTP_201_CREATED)


@router.post(
    path='',
    responses=create_response,
    status_code=status.HTTP_201_CREATED,
)
async def create_application(
    dto: BaseApplication,
    application_service: ApplicationService = Depends(),
) -> Response:
    await application_service.create(dto)
    return Response(status_code=status.HTTP_201_CREATED)
