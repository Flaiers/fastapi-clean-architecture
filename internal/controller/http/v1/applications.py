from internal.usecase.utils import SucessfulResponse as Response
from internal.service.application import ApplicationService
from internal.dto.application import BaseApplication
from internal.entity.application import Application

from fastapi import Depends, APIRouter, status


router = APIRouter()
name = "Create {0}".format(Application.__name__)
responses = Response.get_response(status.HTTP_201_CREATED)


@router.post(
    path="",
    name=name,
    responses=responses,
    status_code=status.HTTP_201_CREATED
)
async def create(
    dto: BaseApplication,
    application_service: ApplicationService = Depends()
) -> Response:
    await application_service.create(dto)
    return Response(status_code=status.HTTP_201_CREATED)
