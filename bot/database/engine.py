"""Async DB engine va sessiya (PHASE 2)."""
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from bot.config import config
from bot.database.models import Base

engine = create_async_engine(f"sqlite+aiosqlite:///{config.db_path}", echo=False)

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db() -> None:
    """Jadvallarni yaratish (oddiy create_all migration)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
