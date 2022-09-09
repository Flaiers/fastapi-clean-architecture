from fastapi import APIRouter

from internal.usecase.utils import SuccessfulResponse

router = APIRouter()


@router.get('', responses=SuccessfulResponse.schema())
async def health() -> SuccessfulResponse:
    return SuccessfulResponse()
