from sqlalchemy.ext.asyncio import AsyncSession

from core.config import postgres_settings
from dependencies.postgres import get_sessionmaker


async def get_postgres_session() -> AsyncSession:
    async with get_sessionmaker(
        user=postgres_settings.user,
        password=postgres_settings.password,
        host=postgres_settings.host,
        port=postgres_settings.port,
        dbname=postgres_settings.dbname
    )() as session:
        yield session
