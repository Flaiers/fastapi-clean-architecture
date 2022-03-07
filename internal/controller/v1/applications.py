from internal.usecase.responses import SucessfulResponse
from internal.dto.application import BaseApplication
from internal.entity.application import Application
from internal.app.database import get_session

from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import Depends, APIRouter
from starlette.status import *


router = APIRouter()
responses = {
    HTTP_201_CREATED: {
        "description": "Successful Response",
        "content": {
            "application/json": {
                "example": {"sucessful": True},
            }
        }
    }
}


@router.post("", name=f"Create {Application.__name__}",             
             status_code=HTTP_201_CREATED,
             responses=responses)
async def create(
    instance: BaseApplication,
    db: AsyncSession = Depends(get_session)
) -> SucessfulResponse:
    instance = Application(**instance.dict())
    db.add(instance)
    await db.commit()
    return SucessfulResponse(status_code=HTTP_201_CREATED)
