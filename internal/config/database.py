from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import Session, scoped_session, sessionmaker
from sqlalchemy import MetaData, create_engine

from internal.usecase.utils import get_session
from . import settings


__all__ = ["init_db", "current_session", "override_session"]


async def init_db(url):
    engine = create_async_engine(
        url, pool_pre_ping=True, future=True
    )
    async with engine.begin() as conn:
        await conn.run_sync(MetaData.create_all)


def async_session(url):
    engine = create_async_engine(
        url, pool_pre_ping=True, future=True
    )
    session_factory = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async def get_session() -> AsyncSession:
        async with session_factory() as session:
            yield session

    return get_session


def sync_session(url) -> Session:
    engine = create_engine(
        url.replace("+asyncpg", ""), pool_pre_ping=True, future=True
    )
    session_factory = sessionmaker(
        engine, autoflush=False, expire_on_commit=False
    )
    return scoped_session(session_factory)


current_session = sync_session(settings.SQLALCHEMY_DATABASE_URI)
override_session = get_session, async_session(settings.SQLALCHEMY_DATABASE_URI)
