from fastapi import APIRouter, Depends, status

from internal.dto.application import BaseApplication
from internal.entity.application import Application
from internal.service.application import ApplicationService
from internal.usecase.utils import SucessfulResponse as Response

router = APIRouter()
responses = Response.get_response(status.HTTP_201_CREATED)


@router.post(
    path="",
    responses=responses,
    status_code=status.HTTP_201_CREATED,
    name="Create {0}".format(Application.__name__)
)
async def create(
    dto: BaseApplication,
    application_service: ApplicationService = Depends()
) -> Response:
    await application_service.create(dto)
    return Response(status_code=status.HTTP_201_CREATED)
