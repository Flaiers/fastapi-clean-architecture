from internal.config.database import init_db


def startup_database(url: str):
    async def wrapper():
        await init_db(url)

    return wrapper
