from functools import wraps

from fastapi import HTTPException, Request, status

from core.globals import COOKIE_PREFIX
from services.jwt import JWTService


def if_token_is_valid(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request: Request = kwargs.get('request')
        jwt_session: JWTService = kwargs.get('jwt_session')

        access_token = request.cookies.get(f'{COOKIE_PREFIX}_access_token')

        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Sign in required!'
            )

        if not await jwt_session.check_access_token(
            access_token=access_token
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Sign in required!'
            )

        return await func(*args, **kwargs)

    return wrapper
