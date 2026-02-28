from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from src.configs.db import postgres_settings

engine = create_async_engine(postgres_settings.db_url)

_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


@asynccontextmanager
async def session():
    _session = _session_factory()
    try:
        yield _session
        await _session.commit()
    except Exception:
        await _session.rollback()
        raise
    finally:
        await _session.close()
