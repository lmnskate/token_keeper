from typing import Annotated

import aiohttp
from fastapi import (APIRouter, Depends, HTTPException, Request, Response,
                     status)
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from crud.common import add_to_db
from crud.user import check_password, get_user_id
from models.models import LogonHistory
from schemas.service_message import ServiceMessageModel
from schemas.user import LocalUserAuthorizeModel
from services.jwt import JWTService, get_jwt_session
from services.oauth import (get_aiohttp_session, get_google_oauth,
                            get_yandex_oauth)
from services.postgres import get_postgres_session
from services.tracer import get_tracer_session
from utils.tokens import create_tokens, set_tokens_to_cookies

router = APIRouter()

tracer = get_tracer_session()


@router.post('/local',
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
    with tracer.start_as_current_span('Checking password'):
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

    with tracer.start_as_current_span('Adding logon record to database'):
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

    with tracer.start_as_current_span('Creating new tokens'):
        access_token, refresh_token = create_tokens(
            jwt_session=jwt_session,
            email=local_user_authorize_model.email
        )

    with tracer.start_as_current_span('Setting new tokens to response headers'):
        set_tokens_to_cookies(
            response=response,
            access_token=access_token,
            refresh_token=refresh_token
        )

    return ServiceMessageModel(
        message='Successfully authorized!'
    )


@router.get('/{service}',
            tags=['Авторизация', 'Внешняя авторизация'],
            summary='Перенаправление пользователя на страницу внешней авторизации',
            description='Перенаправление пользователя на страницу внешнего сервиса авторизации')
async def get_code(
    request: Request,
    service: Annotated[str, ['google', 'yandex']] = None,
    session: aiohttp.ClientSession = Depends(get_aiohttp_session)
) -> RedirectResponse:
    with tracer.start_as_current_span('Redirecting user to Oauth service login page'):
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
