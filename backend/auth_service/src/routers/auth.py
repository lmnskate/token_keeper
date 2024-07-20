import secrets
from typing import Annotated

import aiohttp
from fastapi import (APIRouter, Depends, HTTPException, Request, Response,
                     status)
from fastapi.encoders import jsonable_encoder
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from crud.common import add_to_db
from crud.user import check_email, check_password, get_user_id
from models.models import LogonHistory, User
from schemas.service_message import ServiceMessageModel
from schemas.user import LocalUserAuthorizeModel, LocalUserCreateModel
from services.jwt import JWTService, get_jwt_session
from services.oauth import (get_aiohttp_session, get_google_oauth,
                            get_yandex_oauth)
from services.postgres import get_postgres_session
from utils.tokens import create_tokens, set_tokens_to_cookies

router = APIRouter()


@router.post('/signup/local',
             tags=['Авторизация'],
             summary='Регистрация пользователя',
             description='Регистрация пользователя',
             response_model=ServiceMessageModel,
             response_description='Сообщение об успешной регистрации',
             status_code=status.HTTP_200_OK)
async def create_local_user(
    local_user_create_model: LocalUserCreateModel,
    request: Request,
    response: Response,
    jwt_session: JWTService = Depends(get_jwt_session),
    db_session: AsyncSession = Depends(get_postgres_session)
) -> ServiceMessageModel:
    user = User(**jsonable_encoder(local_user_create_model))

    if not await check_email(
        db_session=db_session,
        email=user.email
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Account with provided email is already exists!'
        )

    access_token, refresh_token = create_tokens(
        jwt_session=jwt_session,
        email=user.email
    )

    set_tokens_to_cookies(
        response=response,
        access_token=access_token,
        refresh_token=refresh_token
    )

    user.refresh_token = refresh_token

    await add_to_db(
        db_session=db_session,
        instance=user
    )

    auth_history = LogonHistory(
        ip=request.client.host,
        user_agent=request.headers.get('User-Agent'),
        user_id=await get_user_id(
            db_session=db_session,
            email=user.email
        )
    )

    await add_to_db(
        db_session=db_session,
        instance=auth_history
    )

    return ServiceMessageModel(
        message='Successfully signed up!'
    )


@router.post('/signin/local',
             tags=['Авторизация'],
             summary='Авторизация пользователя',
             description='Авторизация пользователя',
             response_model=ServiceMessageModel,
             response_description='Сообщение об успешной авторизации',
             status_code=status.HTTP_200_OK)
async def authorize_local_user(
    local_user_authorize_model: LocalUserAuthorizeModel,
    request: Request,
    response: Response,
    jwt_session: JWTService = Depends(get_jwt_session),
    db_session: AsyncSession = Depends(get_postgres_session)
) -> ServiceMessageModel:
    password_check_result = await check_password(
        db_session=db_session,
        email=local_user_authorize_model.email,
        password=local_user_authorize_model.password
    )
    if not password_check_result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Check your login and password!'
        )

    auth_history = LogonHistory(
        ip=request.client.host,
        user_agent=request.headers.get('User-Agent'),
        user_id=await get_user_id(
            db_session=db_session,
            email=local_user_authorize_model.email
        )
    )

    await add_to_db(
        db_session=db_session,
        instance=auth_history
    )

    access_token, refresh_token = create_tokens(
        jwt_session=jwt_session,
        email=local_user_authorize_model.email
    )

    set_tokens_to_cookies(
        response=response,
        access_token=access_token,
        refresh_token=refresh_token
    )

    return ServiceMessageModel(
        message='Successfully authorized!'
    )


@router.get('/signin/{service}',
            tags=['Внешняя авторизация'],
            summary='Перенаправление пользователя на страницу внешней авторизации',
            description='Перенаправление пользователя на страницу внешнего сервиса авторизации')
async def get_code(
    request: Request,
    service: Annotated[str, ['google', 'yandex']] = None,
    session: aiohttp.ClientSession = Depends(get_aiohttp_session)
) -> RedirectResponse:
    if service == 'google':
        google_oauth = get_google_oauth(
            session=session
        )
        return RedirectResponse(
            url=google_oauth.get_login_url()
        )
    elif service == 'yandex':
        yandex_oauth = get_yandex_oauth(
            session=session
        )
        return RedirectResponse(
            url=yandex_oauth.get_login_url()
        )


@router.get('/signup/{service}',
            tags=['Внешняя авторизация'],
            summary='Регистрация пользователя с использованием внешней авторизации',
            description='Регистрация пользователя с использованием внешнего сервиса авторизации',
            response_model=ServiceMessageModel,
            response_description='Сообщение об авторизации, пароль пользователя',
            status_code=status.HTTP_200_OK)
async def create_oauth_user(
    code: str,
    response: Response,
    request: Request,
    service: Annotated[str, ['google', 'yandex']] = None,
    session: aiohttp.ClientSession = Depends(get_aiohttp_session),
    jwt_service: JWTService = Depends(get_jwt_session),
    db_session: AsyncSession = Depends(get_postgres_session)
) -> ServiceMessageModel:
    if service == 'google':
        google_oauth = get_google_oauth(
            session=session
        )
        user_oauth_model = await google_oauth.get_user_data(
            authorization_code=code
        )
    elif service == 'yandex':
        yandex_oauth = get_yandex_oauth(
            session=session
        )
        user_oauth_model = await yandex_oauth.get_user_data(
            authorization_code=code
        )
    else:
        return ServiceMessageModel(
            message='Cannot perform authorization with requested service!'
        )

    # проверяем, существует ли пользователь с email, возвращённым сервисом
    if not await check_email(
            db_session=db_session,
            email=user_oauth_model.email
    ):
        # really???
        return ServiceMessageModel(
            message='Successfully authorized!'
        )

    # регистрируем пользователя
    password = secrets.token_urlsafe(
        nbytes=10
    )

    user = User(
        password=password,
        **user_oauth_model.model_dump(
            exclude=['id']
        )
    )

    await add_to_db(
        db_session=db_session,
        instance=user
    )

    return ServiceMessageModel(
        message=f'Successfully signed up. Your password is {password}, change it immediately.'
    )
