from fastapi import (APIRouter, Depends, HTTPException, Request, Response,
                     status)
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from core.globals import COOKIE_PREFIX
from crud.logon_history import get_auth_history
from crud.user import check_password, get_user_id, update_user_credentials
from schemas.common import Paginator
from schemas.logon_history import LogonHistoryModel
from schemas.service_message import ServiceMessageModel
from schemas.user import ChangePasswordModel
from services.jwt import JWTService, get_jwt_session
from services.postgres import get_postgres_session
from services.tracer import get_tracer_session
from utils.tokens import create_tokens, set_tokens_to_cookies
from utils.wrappers import if_token_is_valid

router = APIRouter()

tracer = get_tracer_session()


@router.get('/refresh_tokens',
            tags=['Аккаунт'],
            summary='Обновление токенов пользователя',
            description='Обновление ACCESS_TOKEN и REFRESH_TOKEN пользователя',
            response_model=ServiceMessageModel,
            response_description='Сообщение об успешном обновлении токенов пользователя',
            status_code=status.HTTP_200_OK)
@if_token_is_valid
async def refresh_tokens(
    request: Request,
    response: Response,
    jwt_session: JWTService = Depends(get_jwt_session),
    db_session: AsyncSession = Depends(get_postgres_session)
) -> ServiceMessageModel:
    old_access_token = request.cookies.get(f'{COOKIE_PREFIX}_access_token')
    old_refresh_token = request.cookies.get(f'{COOKIE_PREFIX}_refresh_token')

    with tracer.start_as_current_span('Extracting user email from access token'):
        email = jwt_session.get_data_from_token(
            token=old_refresh_token
        )

    with tracer.start_as_current_span('Disabling old access token'):
        await jwt_session.disable_access_token(
            access_token=old_access_token
        )

    with tracer.start_as_current_span('Creating new tokens'):
        new_access_token, new_refresh_token = create_tokens(
            jwt_session=jwt_session,
            email=email
        )

    with tracer.start_as_current_span('Setting new tokens to response headers'):
        set_tokens_to_cookies(
            response=response,
            access_token=new_access_token,
            refresh_token=new_refresh_token
        )

    return ServiceMessageModel(
        message='Tokens refreshed successfully!'
    )


@router.post('/change_password',
             tags=['Аккаунт'],
             summary='Изменение пароля пользователя',
             description='Изменение авторизованным пользователем своего пароля',
             response_model=ServiceMessageModel,
             response_description='Сообщение об успешной смене пароля')
@if_token_is_valid
async def change_password(
    change_password_model: ChangePasswordModel,
    request: Request,
    response: Response,
    jwt_session: JWTService = Depends(get_jwt_session),
    db_session: AsyncSession = Depends(get_postgres_session)
) -> ServiceMessageModel:
    old_access_token = request.cookies.get(f'{COOKIE_PREFIX}_access_token')

    with tracer.start_as_current_span('Extracting user email from access token'):
        email = await jwt_session.get_data_from_access_token(
            access_token=old_access_token
        )

    with tracer.start_as_current_span('Checking old password'):
        password_check_result = await check_password(
            db_session=db_session,
            email=email,
            password=change_password_model.old_password
        )
        if not password_check_result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Password didn\'t match!'
            )

    with tracer.start_as_current_span('Disabling old access token'):
        await jwt_session.disable_access_token(
            access_token=old_access_token
        )

    with tracer.start_as_current_span('Creating new tokens'):
        new_access_token, new_refresh_token = create_tokens(
            jwt_session=jwt_session,
            email=email
        )

    with tracer.start_as_current_span('Setting new tokens to response headers'):
        set_tokens_to_cookies(
            response=response,
            access_token=new_access_token,
            refresh_token=new_refresh_token
        )

    with tracer.start_as_current_span('Updating password in database'):
        await update_user_credentials(
            db_session=db_session,
            email=email,
            new_password=change_password_model.new_password,
            new_refresh_token=new_refresh_token
        )

    return ServiceMessageModel(
        message='Password successfully updated!'
    )


@router.get('/logon_history',
            tags=['Аккаунт'],
            summary='История авторизаций пользователя',
            description='Просмотр истории авторизаций пользователя',
            response_model=list[LogonHistoryModel],
            response_description='История авторизаций пользователя',
            status_code=status.HTTP_200_OK)
@if_token_is_valid
async def get_history(
    request: Request,
    paginator: Paginator = Depends(Paginator),
    jwt_session: JWTService = Depends(get_jwt_session),
    db_session: AsyncSession = Depends(get_postgres_session)
) -> list[LogonHistoryModel]:
    with tracer.start_as_current_span('Extracting user email from access token'):
        email = await jwt_session.get_data_from_access_token(
            access_token=request.cookies.get(f'{COOKIE_PREFIX}_access_token')
        )

    with tracer.start_as_current_span('Extracting user id from database'):
        user_id = await get_user_id(
            db_session=db_session,
            email=email
        )

    with tracer.start_as_current_span('Extracting rows from database'):
        histories = await get_auth_history(
            db_session=db_session,
            user_id=user_id,
            page_number=paginator.page_number,
            page_size=paginator.page_size
        )

    return [LogonHistoryModel(**jsonable_encoder(history)) for history in histories]


@router.get('/logout',
            tags=['Аккаунт'],
            summary='Выход пользователя из учетной записи',
            description='Выход авторизованного пользователя из учетной записи',
            response_model=ServiceMessageModel,
            response_description='Сообщение об успешном выходе из учетной записи',
            status_code=status.HTTP_200_OK)
@if_token_is_valid
async def logout(
    request: Request,
    jwt_session: JWTService = Depends(get_jwt_session)
) -> ServiceMessageModel:
    old_access_token = request.cookies.get(f'{COOKIE_PREFIX}_access_token')

    with tracer.start_as_current_span('Disabling old access token'):
        await jwt_session.disable_access_token(
            access_token=old_access_token
        )

    return ServiceMessageModel(
        message='Logout successfully!'
    )
