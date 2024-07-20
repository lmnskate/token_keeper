import sys
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from core.config import auth_api_settings, postgres_settings, redis_settings
from dependencies import postgres, redis
from routers import account, auth
from rpc.authenticator_server.server import get_authenticator_server
from services import oauth


@asynccontextmanager
async def lifespan(
    app: FastAPI
):
    redis_session = await redis.get_redis(
        host=redis_settings.host,
        port=redis_settings.port
    )

    postgres_session = postgres.get_sessionmaker(
        user=postgres_settings.user,
        password=postgres_settings.password,
        host=postgres_settings.host,
        port=postgres_settings.port,
        dbname=postgres_settings.dbname,
    )()

    aiohttp_session = oauth.get_aiohttp_session()

    authenticator_server = get_authenticator_server(
        port=auth_api_settings.authenticator_port
    )
    await authenticator_server.start()

    yield

    await redis_session.close()

    await postgres_session.close()

    await aiohttp_session.aclose()

    await authenticator_server.wait_for_termination(
        timeout=5
    )


app = FastAPI(
    title='API cервиса авторизации',
    description='API для авторизации пользователей',
    version='1.0.0',
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)


app.include_router(
    router=auth.router,
    prefix='/api/v1/auth'
)
app.include_router(
    router=account.router,
    prefix='/api/v1/account'
)

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=int(sys.argv[1]),
    )
