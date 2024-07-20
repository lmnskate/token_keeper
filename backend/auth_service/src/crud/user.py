from models.models import User
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def check_email(
    db_session: AsyncSession,
    email: str
) -> bool:
    '''
    Функция для проверки того, существует ли в БД пользователь с искомым адресом почты

    :param email: искомый адрес почты
    '''

    result = await db_session.execute(
        select(User.email)
        .where(User.email == email)
    )

    if not result.scalars().all():
        return True

    return False


async def check_password(
    db_session: AsyncSession,
    email: str,
    password: str
) -> bool:
    '''
    Функция для проверки введенного клиентом пароля

    :param email: введенный email
    :param password: введенный пароль
    '''

    result = await db_session.execute(
        select(User)
        .where(User.email == email)
    )

    user = result.scalars().first()
    if user:
        return user.check_password(password)

    return False


async def get_user_id(
    db_session: AsyncSession,
    email: str
) -> str:
    '''
    Функция для получения id пользователя по email

    :param email: искомый email
    '''

    result = await db_session.execute(
        select(User.id)
        .where(User.email == email)
    )

    return result.scalars().first()


async def update_user_credentials(
    db_session: AsyncSession,
    email: str,
    new_password: str,
    new_refresh_token: str
) -> None:
    '''
    Функция для обновления аутентификационных данных пользователя

    :param email: email обновляемого пользователя
    :param new_password: новый пароль
    :param new_refresh_token: новый refresh_token
    '''

    result = await db_session.execute(
        select(User)
        .where(User.email == email)
    )

    user = result.scalars().first()
    user.set_updated_password(new_password)
    user.refresh_token = new_refresh_token

    await db_session.commit()
