from pydantic_settings import BaseSettings, SettingsConfigDict


class AuthAPISettings(BaseSettings):
    '''Класс, содержащий настройки сервиса авторизации'''

    model_config = SettingsConfigDict(env_prefix='AUTH_API_')
    authenticator_port: int


class PostgresSettings(BaseSettings):
    '''Класс, содержащий настройки для подключения к БД Postgres сервиса авторизации'''

    model_config = SettingsConfigDict(env_prefix='AUTH_POSTGRES_')
    host: str
    port: int
    user: str
    password: str
    dbname: str


class RedisSettings(BaseSettings):
    '''Класс, содержащий настройки для подключения к хранилищу Redis сервиса авторизации'''

    model_config = SettingsConfigDict(env_prefix='AUTH_REDIS_')
    host: str
    port: int


class JWTSettings(BaseSettings):
    '''Класс, содержащий настройки генерации JWT-токенов'''

    model_config = SettingsConfigDict(env_prefix='AUTH_JWT_')
    secret: str
    access_lifetime: int
    refresh_lifetime: int


class GoogleSettings(BaseSettings):
    '''Класс, содержащий настройки подключения к сервису авторизации Google'''

    model_config = SettingsConfigDict(env_prefix='GOOGLE_')
    client_id: str
    client_secret: str
    redirect_uri: str


class YandexSettings(BaseSettings):
    '''Класс, содержащий настройки подключения к сервису авторизации Yandex'''

    model_config = SettingsConfigDict(env_prefix='YANDEX_')
    client_id: str
    client_secret: str
    redirect_uri: str


class JaegerSettings(BaseSettings):
    '''Класс,содержащий настройки подключения к jaeger'''

    model_config = SettingsConfigDict(env_prefix='JAEGER_')
    enable_tracer: bool = True
    host: str
    http_port: int


class LogstashSettings(BaseSettings):
    """Класс, содержащий настройки для подключения к Logstash"""

    model_config = SettingsConfigDict(env_prefix="LOGSTASH_")
    host: str
    port: int


auth_api_settings = AuthAPISettings()
postgres_settings = PostgresSettings()
redis_settings = RedisSettings()
jwt_settings = JWTSettings()
google_settings = GoogleSettings()
yandex_settings = YandexSettings()
jaeger_settings = JaegerSettings()
logstash_settings = LogstashSettings()
