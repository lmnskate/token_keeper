from typing import Tuple

from core.globals import COOKIE_PREFIX
from fastapi import Response
from services.jwt import JWTService


def create_tokens(
    jwt_session: JWTService,
    email: str
) -> Tuple[str, str]:
    '''
    Функция создания токенов для конкретного пользователя

    :param email: email пользователяя
    '''

    access_token = jwt_session.create_access_token(
        email=email
    )

    refresh_token = jwt_session.create_refresh_token(
        email=email
    )

    return access_token, refresh_token


def set_tokens_to_cookies(
    response: Response,
    access_token: str,
    refresh_token: str
) -> None:
    '''
    Функция выставления cookie, содержащих токены, в ответе сервиса

    :param access_token: access_token
    :param refresh_token: refresh_token
    '''

    response.set_cookie(
        key=f'{COOKIE_PREFIX}_access_token',
        value=access_token
    )

    response.set_cookie(
        key=f'{COOKIE_PREFIX}_refresh_token',
        value=refresh_token
    )
