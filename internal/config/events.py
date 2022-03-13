from .database import init_db
from . import settings


__all__ = ["startup_event"]


async def startup_event():
    await init_db(settings.SQLALCHEMY_DATABASE_URI)
