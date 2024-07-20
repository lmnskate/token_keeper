from dependencies.postgres import Base
from sqlalchemy.ext.asyncio import AsyncSession


async def add_to_db(
    db_session: AsyncSession,
    instance: Base
) -> None:
    '''
    Функция для добавления данных БД

    :param instance: данные экземпляра добавляемой сущности
    '''

    db_session.add(instance)
    await db_session.commit()
    await db_session.refresh(instance)
