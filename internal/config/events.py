from internal.config.database import create_database


def startup_database(url: str):
    async def wrapper():
        await create_database(url)

    return wrapper
