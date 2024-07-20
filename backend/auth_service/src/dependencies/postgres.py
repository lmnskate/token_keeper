from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


def get_sessionmaker(
    user: str,
    password: str,
    host: str,
    port: str,
    dbname: str
) -> sessionmaker:
    engine = create_async_engine(
        f'postgresql+asyncpg://{user}:{password}@{host}:{port}/{dbname}',
        echo=False,
        future=True
    )

    return sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
