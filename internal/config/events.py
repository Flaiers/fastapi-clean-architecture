from internal.config import settings
from internal.config.database import init_db


async def startup_event():
    await init_db(settings.SQLALCHEMY_DATABASE_URI)
