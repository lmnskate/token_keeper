from pydantic_settings import BaseSettings, SettingsConfigDict


class AuthAPISettings(BaseSettings):
    '''Класс, содержащий настройки сервиса авторизации'''

    model_config = SettingsConfigDict(env_prefix='AUTH_API_')
    authenticator_port: int = 9000


class PostgresSettings(BaseSettings):
    '''Класс, содержащий настройки для подключения к БД Postgres сервиса авторизации'''

    model_config = SettingsConfigDict(env_prefix='AUTH_POSTGRES_')
    host: str = '127.0.0.1'
    port: int = 5432
    user: str = 'auth_db_admin'
    password: str = '123qwe'
    dbname: str = 'auth_db'


class RedisSettings(BaseSettings):
    '''Класс, содержащий настройки для подключения к хранилищу Redis сервиса авторизации'''

    model_config = SettingsConfigDict(env_prefix='AUTH_REDIS_')
    host: str = '127.0.0.1'
    port: int = 6379


class JWTSettings(BaseSettings):
    '''Класс, содержащий настройки генерации JWT-токенов'''

    model_config = SettingsConfigDict(env_prefix='AUTH_JWT_')
    secret: str = 'mnbvcxz123'
    access_lifetime: int = 15
    refresh_lifetime: int = 15


class GoogleSettings(BaseSettings):
    '''Класс, содержащий настройки подключения к сервису авторизации Google'''

    model_config = SettingsConfigDict(env_prefix='GOOGLE_')
    client_id: str = '111'
    client_secret: str = '111'
    redirect_uri: str = '111'


class YandexSettings(BaseSettings):
    '''Класс, содержащий настройки подключения к сервису авторизации Yandex'''

    model_config = SettingsConfigDict(env_prefix='YANDEX_')
    client_id: str = '5ddd52440165447298a2dd141baebb29'
    client_secret: str = '5dec604416ba4e528d8fee70eaf3d51d'
    redirect_uri: str = 'http://127.0.0.1:5000/api/v1/auth/signup/yandex'


auth_api_settings = AuthAPISettings()
postgres_settings = PostgresSettings()
redis_settings = RedisSettings()
jwt_settings = JWTSettings()
google_settings = GoogleSettings()
yandex_settings = YandexSettings()
