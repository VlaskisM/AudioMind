# src/db/relational/db.py
# Реализует асинхронное подключение к PostgreSQL
# Использует SQLAlchemy и AsyncPG


from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from src.configs.db import postgres_settings

# Подключение к PostgreSQL
engine = create_async_engine(postgres_settings.db_url)

# Фабрика сессий - каждый запрос получает свою сессию
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Базовый класс для всех моделей
class Base(DeclarativeBase):
    pass

async def init_db():
    from src.db.relational.entities.recording import Recording  

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session