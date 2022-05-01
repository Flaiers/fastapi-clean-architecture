from internal.config.database import init_db


def startup_event(settings):
    async def wrapper():
        await init_db(settings.SQLALCHEMY_DATABASE_URI)

    return wrapper
