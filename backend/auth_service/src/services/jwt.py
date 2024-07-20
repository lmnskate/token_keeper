from datetime import datetime, timedelta

from core.config import jwt_settings
from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from jose.constants import ALGORITHMS
from redis.asyncio.client import Redis
from services.redis import get_redis_session


class BasicJWTService:
    '''
    Базовый класс для генерации и валидации JWT-токенов
    '''

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={
            'WWW-Authenticate': 'Bearer'
        }
    )

    def __init__(self):
        self.settings = jwt_settings
        self.algorithm = ALGORITHMS.HS256

    def _create_token(
        self,
        email: str,
        expires_delta: timedelta
    ) -> str:
        '''
        Функция генерации токена

        :param email: email пользователя
        :param expires_delta: время жизни токена
        '''

        expire = datetime.now() + expires_delta
        to_encode = {
            'sub': email,
            'exp': expire
        }

        encoded_jwt = jwt.encode(
            claims=to_encode,
            key=self.settings.secret,
            algorithm=self.algorithm
        )

        return encoded_jwt

    def create_access_token(
        self,
        *args,
        **kwargs
    ) -> str:
        '''
        Функция генерации access_token
        '''

        return self._create_token(
            *args,
            **kwargs,
            expires_delta=timedelta(
                days=self.settings.access_lifetime
            ),
        )

    def create_refresh_token(
        self,
        *args,
        **kwargs
    ) -> str:
        '''
        Функция генерации refresh_token
        '''

        return self._create_token(
            *args,
            **kwargs,
            expires_delta=timedelta(
                days=self.settings.refresh_lifetime
            ),
        )

    def check_token(
        self,
        token: str
    ) -> bool:
        '''
        Функция проверки валидности токена

        :param token: проверяемый токен
        '''

        try:
            jwt.decode(
                token=token,
                key=self.settings.secret,
                algorithms=[self.algorithm]
            )
        except JWTError:
            return False

        return True

    def get_data_from_token(
        self,
        token: str
    ) -> tuple[str, str | None]:
        '''
        Функция извлечения данных, содержащихся в токене

        :param token: проверяемый токен
        '''

        try:
            payload = jwt.decode(
                token=token,
                key=self.settings.secret,
                algorithms=[self.algorithm]
            )

        except JWTError:
            raise self.credentials_exception

        email = payload.get('sub')

        if email is None:
            raise self.credentials_exception

        return email


class JWTService(BasicJWTService):
    '''
    Класс для работы с JWT, реализующий подключение к Redis
    '''

    def __init__(
        self,
        redis_session: Redis,
        *args,
        **kwargs
    ):
        self.redis_session = redis_session
        super().__init__(*args, **kwargs)

    async def is_token_invalid(
        self,
        token: str
    ) -> bool:
        '''
        Проверяет наличие токена среди базы невалидных токенов в Redis

        :param token: проверяемый токен
        '''

        result = await self.redis_session.get(token)
        return bool(result)

    async def disable_access_token(
        self,
        access_token=str
    ) -> None:
        '''
        Функция для отправки неактуального access_token в Redis

        :param access_token: отправляемый access_token
        '''

        return await self.redis_session.set(
            name=access_token,
            value='true',
            ex=timedelta(
                minutes=self.settings.access_lifetime
            ),
        )

    async def check_access_token(
        self,
        access_token: str
    ) -> bool:
        '''
        Функция проверки валидности и актуальности access_token

        :param access_token: проверяемый access_token
        '''

        if not self.check_token(
            token=access_token
        ):
            return False
        elif await self.is_token_invalid(
            token=access_token
        ):
            return False

        return True

    async def get_data_from_access_token(
        self,
        access_token: str
    ) -> tuple[str, str | None]:
        '''
        Функция получения данных из access_token

        :param access_token: проверяемый access_token
        '''

        if not await self.check_access_token(
            access_token=access_token
        ):
            raise self.credentials_exception

        return super().get_data_from_token(
            token=access_token
        )


def get_jwt_session(
    redis_session=Depends(get_redis_session)
) -> JWTService:
    return JWTService(redis_session)
