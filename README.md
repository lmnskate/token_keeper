# Сервис хранения токенов
## Переменные окружения
### Сервис авторизации
| Переменная                    | Описание                                     | Пример                                  |
|-------------------------------|----------------------------------------------|-----------------------------------------|
| `AUTH_API_PORT`               | Порт сервиса авторизации                     | `5000`                                  |
| `AUTH_API_AUTHENTICATOR_PORT` | Порт gRPC-сервера сервиса авторизации        | `9000`                                  |
| `AUTH_POSTGRES_HOST`          | Хост БД сервиса авторизации                  | `auth_postgres`                         |
| `AUTH_POSTGRES_PORT`          | Порт БД сервиса авторизации                  | `5432`                                  |
| `AUTH_POSTGRES_DBNAME`        | Название БД сервиса авторизации              | `auth_db`                               |
| `AUTH_POSTGRES_USER`          | Имя администратора БД сервиса авторизации    | `auth_db_admin`                         |
| `AUTH_POSTGRES_PASSWORD`      | Пароль администратора БД сервиса авторизации | `********`                              |
| `AUTH_REDIS_HOST`             | Хост кеша сервиса авторизации                | `auth_redis`                            |
| `AUTH_REDIS_PORT`             | Порт кеша сервиса авторизации                | `6379`                                  |
| `AUTH_JWT_SECRET`             | Секрет генерации JWT-токенов                 | `********`                              |
| `AUTH_JWT_ACCESS_LIFETIME`    | Время жизни access-токена, минут             | `15`                                    |
| `AUTH_JWT_REFRESH_LIFETIME`   | Время жизни refresh-токена, дней             | `15`                                    |
| `YANDEX_CLIENT_ID`            | CLIENT_ID для авторизации через Яндекс       | `********`                              |
| `YANDEX_CLIENT_SECRET`        | Секрет для авторизации через Яндекс          | `********`                              |
| `YANDEX_REDIRECT_URI`         | Redirect URL при авторизации через Яндекс    | `http://127.0.0.1/api/v1/signup/yandex` |
| `GOOGLE_CLIENT_ID`            | CLIENT_ID для авторизации через Google       | `********`                              |
| `GOOGLE_CLIENT_SECRET`        | Секрет для авторизации через Google          | `********`                              |
| `GOOGLE_REDIRECT_URI`         | Redirect URL при авторизации через Google    | `http://127.0.0.1/api/v1/signup/google` |

### Система логирования и трейсинга
| Переменная             | Описание                | Пример           |
|------------------------|-------------------------|------------------|
| `JAEGER_HOST`          | Хост трейсера           | `logging_jaeger` |
| `JAEGER_ENABLE_TRACER` | Включить трейсинг       | `True`           |
| `JAEGER_HTTP_PORT`     | Служебный порт трейсера | `6831`           |
| `JAEGER_UI_PORT`       | UI-порт трейсера        | `16686`          |