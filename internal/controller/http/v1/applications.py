from internal.utils.responses import SucessfulResponse as Response
from internal.service.application import ApplicationService
from internal.dto.application import BaseApplication
from internal.entity.application import Application

from fastapi import Depends, APIRouter
from starlette.status import *


router = APIRouter()
responses = Response.get_response(HTTP_201_CREATED)


@router.post("", name=f"Create {Application.__name__}",             
             status_code=HTTP_201_CREATED,
             responses=responses)
async def create(
    schema: BaseApplication,
    applicationService: ApplicationService = Depends()
) -> Response:
    await applicationService.create(schema)
    return Response(status_code=HTTP_201_CREATED)
