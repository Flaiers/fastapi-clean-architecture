from contextlib import asynccontextmanager
from typing import Any, AsyncContextManager, AsyncGenerator, Callable

from sqlalchemy import create_engine, orm
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from internal.config import settings
from internal.entity.base import Base
from internal.usecase.utils import get_session

AsyncSessionGenerator = AsyncGenerator[AsyncSession, None]


async def create_database(url: str) -> None:
    engine = create_async_engine(
        url, pool_pre_ping=True, future=True,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await engine.dispose()


def async_session(
    url: str, *, wrap: Callable[..., Any] | None = None,
) -> Callable[..., AsyncSessionGenerator] | AsyncContextManager[Any]:
    engine = create_async_engine(
        url, pool_pre_ping=True, future=True,
    )
    factory = orm.sessionmaker(
        engine, class_=AsyncSession, autoflush=False, expire_on_commit=False,
    )

    async def get_session() -> AsyncSessionGenerator:  # noqa: WPS430, WPS442
        async with factory() as session:
            yield session

    return get_session if wrap is None else wrap(get_session)


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
context_session = async_session(settings.DATABASE_URI, wrap=asynccontextmanager)
