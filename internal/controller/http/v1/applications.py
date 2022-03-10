from internal.usecase.responses import SucessfulResponse as Response
from internal.dto.application import BaseApplication
from internal.entity.application import Application
from internal.app.database import get_session

from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import Depends, APIRouter
from starlette.status import *


router = APIRouter()
responses = Response.get_response(HTTP_201_CREATED)


@router.post("", name=f"Create {Application.__name__}",             
             status_code=HTTP_201_CREATED,
             responses=responses)
async def create(
    instance: BaseApplication,
    db: AsyncSession = Depends(get_session)
) -> Response:
    instance = Application(**instance.dict())
    db.add(instance)
    await db.commit()
    return Response(status_code=HTTP_201_CREATED)
