from typing import AsyncGenerator, Callable

from sqlalchemy import create_engine, orm
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from internal.config import settings
from internal.entity.base import Base
from package.sqlalchemy import get_session

AsyncSessionGenerator = AsyncGenerator[AsyncSession, None]


async def init_db(url: str) -> None:
    engine = create_async_engine(
        url, pool_pre_ping=True, future=True,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await engine.dispose()


def async_session(url: str) -> Callable[..., AsyncSessionGenerator]:
    engine = create_async_engine(
        url, pool_pre_ping=True, future=True,
    )
    factory = orm.sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False,
    )

    async def get_session() -> AsyncSessionGenerator:  # noqa: WPS430, WPS442
        async with factory() as session:
            yield session

    return get_session


def sync_session(url: str) -> orm.scoped_session:
    engine = create_engine(
        url, pool_pre_ping=True, future=True,
    )
    factory = orm.sessionmaker(
        engine, autoflush=False, expire_on_commit=False,
    )
    return orm.scoped_session(factory)


override_session = get_session, async_session(settings.DATABASE_URI)
current_session = sync_session(settings.DATABASE_URI.replace('+asyncpg', ''))
