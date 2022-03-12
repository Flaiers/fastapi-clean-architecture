from internal.config.database import init_db


__all__ = ["startup_event"]


async def startup_event():
    await init_db()
