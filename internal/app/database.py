from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import Session, scoped_session, sessionmaker
from sqlalchemy import create_engine
import sqlalchemy as sa

from .config import settings


async_engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True, future=True
)
sync_engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI.replace("+asyncpg", ""),
    pool_pre_ping=True, future=True
)
current_session: Session = scoped_session(sessionmaker(
    sync_engine, autoflush=False, expire_on_commit=False
))


@as_declarative()
class Base:

    __name__: str

    @declared_attr
    def __tablename__(cls) -> str:
        return f"{cls.__name__.lower()}s"

    id = sa.Column(sa.Integer, primary_key=True, index=True)


async def init_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
    async_session = sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
