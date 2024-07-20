import aiohttp
from fastapi import Depends

from core.config import GoogleSettings, YandexSettings
from schemas.user import UserOauthModel


class OauthService:
    '''Класс, обеспечивающий механизм получения данных пользователя от сервиса внешней авторизации'''

    def __init__(
        self,
        aiohttp_session: aiohttp.ClientSession
    ):
        self.session = aiohttp_session

    async def get_user_data(
        self,
        authorization_code: str
    ) -> UserOauthModel:
        '''
        Функция для получения форматированных данных пользователя из сервиса внешней авторизации

        :param authorization_code: код авторизации, полученный от сервиса внешней авторизации
        :return: модель пользователя
        '''

        oauth_token = await self._get_oauth_token(
            authorization_code=authorization_code
        )

        user_data = await self._fetch_user_data(
            oauth_token=oauth_token
        )

        return self._transform_user_data(
            user_data=user_data
        )

    async def _get_oauth_token(
        self,
        authorization_code: str
    ) -> str:
        '''
        Функция для получения токена от сервиса внешней авторизации

        :param authorization_code: код авторизации, полученный от сервиса внешней авторизации
        :return: oauth-токен
        '''

        query = {
            'grant_type': 'authorization_code',
            'code': authorization_code,
            'client_id': self.client_settings.client_id,
            'client_secret': self.client_settings.client_secret,
            'redirect_uri': self.client_settings.redirect_uri,
        }

        async with self.session.post(
            url=self.token_url,
            data=query
        ) as resp:
            if not resp.ok:
                raise aiohttp.ClientResponseError(
                    request_info=resp.request_info,
                    history=None
                )

            data = await resp.json()
            return data['access_token']

    async def _fetch_user_data(
        self,
        oauth_token: str
    ) -> dict:
        '''
        Функция для получения данных о пользователе от сервиса внешней авторизации

        :param oauth_token: oauth-токен
        :return: данные авторизуемого пользователя
        '''

        headers = self._get_header(
            oauth_token=oauth_token
        )

        async with self.session.get(
            url=self.oauth_url,
            headers=headers
        ) as resp:
            if not resp.ok:
                raise aiohttp.ClientResponseError(
                    request_info=resp.request_info,
                    history=None
                )

            return await resp.json()

    def _transform_user_data(
        self,
        user_data: dict
    ) -> UserOauthModel:
        '''
        Функция для форматирования полученных данных пользователя в модель пользователя

        :param user_data: данные пользователя, полученные из сервиса внешней авторизации
        :return: модель пользователя
        '''

        return UserOauthModel(**user_data)

    def _get_header(
        self,
        oauth_token
    ) -> dict:
        return {
            'Authorization': f'OAuth {oauth_token}'
        }


class YandexOauth(OauthService):
    '''Класс, обеспечивающий механизм получения данных пользователя от сервиса внешней авторизации Yandex'''

    oauth_url = 'https://login.yandex.ru/info'
    token_url = 'https://oauth.yandex.ru/token'
    client_settings = YandexSettings()

    def get_login_url(self) -> str:
        '''Функция для получения url, ведущего на страницу авторизации в сервисе Yandex'''

        return f'https://oauth.yandex.ru/authorize?response_type=code&client_id={self.client_settings.client_id}'


class GoogleOauth(OauthService):
    '''Класс, обеспечивающий механизм получения данных пользователя от сервиса внешней авторизации Google'''

    oauth_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
    token_url = 'https://accounts.google.com/o/oauth2/token'
    client_settings = GoogleSettings()

    def get_login_url(self) -> str:
        '''Функция для получения url, ведущего на страницу авторизации в сервисе Google'''

        return f'https://accounts.google.com/o/oauth2/auth?response_type=code&client_id={self.client_settings.client_id}&redirect_uri={self.client_settings.redirect_uri}&scope=openid%20profile%20email&access_type=offline'

    def _get_header(
        self,
        oauth_token: str
    ) -> dict:
        '''
        Функция для получения заголовка, необходимого для получения данных пользователя в сервисе Google

        :param oauth_token: oauth-токен
        :return: заголовок
        '''

        return {
            'Authorization': f'Bearer {oauth_token}'
        }


async def get_aiohttp_session():
    async with aiohttp.ClientSession() as session:
        yield session


def get_google_oauth(
    session: aiohttp.ClientSession = Depends(get_aiohttp_session)
):
    return GoogleOauth(session)


def get_yandex_oauth(
    session: aiohttp.ClientSession = Depends(get_aiohttp_session)
):
    return YandexOauth(session)
