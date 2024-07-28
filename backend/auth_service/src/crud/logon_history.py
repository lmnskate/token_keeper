from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.models import LogonHistory


async def get_auth_history(
    db_session: AsyncSession,
    user_id: str,
    page_number: int,
    page_size: int
) -> list[LogonHistory]:
    '''
    Функция для получения историй авторизаций пользователя

    :param user_id: ID проверяемого пользователя
    :param page_number: номер страницы
    :param page_size: размер страницы
    '''

    offset_value = (page_number - 1) * page_size
    result = await db_session.execute(
        select(LogonHistory)
        .where(LogonHistory.user_id == user_id)
        .offset(offset_value)
        .limit(page_size)
    )

    return result.scalars().all()
