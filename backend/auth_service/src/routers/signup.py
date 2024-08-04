import secrets
from typing import Annotated

import aiohttp
from fastapi import (APIRouter, Depends, HTTPException, Request, Response,
                     status)
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from crud.common import add_to_db
from crud.user import check_email, get_user_id
from models.models import LogonHistory, User
from schemas.service_message import ServiceMessageModel
from schemas.user import LocalUserCreateModel
from services.jwt import JWTService, get_jwt_session
from services.oauth import (get_aiohttp_session, get_google_oauth,
                            get_yandex_oauth)
from services.postgres import get_postgres_session
from services.tracer import get_tracer_session
from utils.tokens import create_tokens, set_tokens_to_cookies

router = APIRouter()

tracer = get_tracer_session()


@router.post('/local',
             tags=['Регистрация'],
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

    with tracer.start_as_current_span('Checking if email is already claimed'):
        if not await check_email(
            db_session=db_session,
            email=user.email
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Account with provided email is already exists!'
            )

    with tracer.start_as_current_span('Creating tokens'):
        access_token, refresh_token = create_tokens(
            jwt_session=jwt_session,
            email=user.email
        )

    with tracer.start_as_current_span('Setting tokens to response headers'):
        set_tokens_to_cookies(
            response=response,
            access_token=access_token,
            refresh_token=refresh_token
        )

    user.refresh_token = refresh_token

    with tracer.start_as_current_span('Adding user record to database'):
        await add_to_db(
            db_session=db_session,
            instance=user
        )

    with tracer.start_as_current_span('Adding logon record to database'):
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


@router.get('/{service}',
            tags=['Регистрация', 'Внешняя регистрация'],
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
    db_session: AsyncSession = Depends(get_postgres_session)
) -> ServiceMessageModel:
    with tracer.start_as_current_span('Getting Oauth authorization code'):
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
    with tracer.start_as_current_span('Checking if user with this email is already exists'):
        if not await check_email(
                db_session=db_session,
                email=user_oauth_model.email
        ):
            # really???
            return ServiceMessageModel(
                message='Successfully authorized!'
            )

    # регистрируем пользователя
    with tracer.start_as_current_span('Creating temporary password'):
        password = secrets.token_urlsafe(
            nbytes=10
        )

    with tracer.start_as_current_span('Adding user record to database'):
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
