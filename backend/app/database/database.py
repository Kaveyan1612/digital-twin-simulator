from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.logging import logger
import os


engine = None
async_engine = None
async_session_factory = None


def get_database_url() -> str:
    url = settings.database_url
    if url.startswith("sqlite"):
        return url.replace("sqlite://", "sqlite+aiosqlite://")
    return url


def init_db():
    global engine, async_engine, async_session_factory
    
    db_url = settings.database_url
    async_db_url = get_database_url()
    
    engine = create_engine(db_url, echo=settings.app_env == "development")
    async_engine = create_async_engine(async_db_url, echo=settings.app_env == "development")
    async_session_factory = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)
    
    SQLModel.metadata.create_all(engine)
    logger.info(f"Database initialized: {db_url}")


@asynccontextmanager
async def get_async_session():
    if async_session_factory is None:
        init_db()
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_session():
    if engine is None:
        init_db()
    with Session(engine) as session:
        yield session


async def close_db():
    global async_engine
    if async_engine:
        await async_engine.dispose()
        logger.info("Database connections closed")