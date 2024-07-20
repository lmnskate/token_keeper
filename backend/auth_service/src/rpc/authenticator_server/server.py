from concurrent import futures

import grpc

from core.config import postgres_settings
from crud.user import get_user_id
from dependencies import postgres
from rpc.authenticator_server.types import (authenticator_pb2,
                                            authenticator_pb2_grpc)
from services.jwt import get_jwt_session
from services.redis import get_redis_session


class Authenticator(authenticator_pb2_grpc.AuthenticatorServicer):
    '''Класс сервисера аутентификации'''

    async def CheckToken(
        self,
        request: authenticator_pb2.Token,
        contexts
    ) -> authenticator_pb2.TokenValidity:
        '''Функция проверки валидности токена'''

        jwt_session = get_jwt_session(
            redis_session=await get_redis_session()
        )

        return authenticator_pb2.TokenValidity(
            is_valid=await jwt_session.check_access_token(
                access_token=request.token
            )
        )

    async def GetUserID(
        self,
        request: authenticator_pb2.Token,
        context
    ) -> authenticator_pb2.UserID:
        '''Функция извлечения ID пользователя из предъявленного токена'''

        async with postgres.get_sessionmaker(
            user=postgres_settings.user,
            password=postgres_settings.password,
            host=postgres_settings.host,
            port=postgres_settings.port,
            dbname=postgres_settings.dbname,
        )() as db_session:
            jwt_session = get_jwt_session(
                redis_session=await get_redis_session()
            )

            email = await jwt_session.get_data_from_access_token(
                access_token=request.token
            )

            user_id = await get_user_id(
                db_session=db_session,
                email=email
            )

            return authenticator_pb2.UserID(
                user_id=str(user_id)
            )


def get_authenticator_server(
    port: int
) -> grpc.Server:
    '''
    Функция инициализации grpc-сервера аутентицикации

    :param port: порт запускаемого сервера
    '''

    server = grpc.aio.server(
        futures.ThreadPoolExecutor(
            max_workers=10
        )
    )

    authenticator_pb2_grpc.add_AuthenticatorServicer_to_server(
        servicer=Authenticator(),
        server=server
    )

    server.add_insecure_port(f'[::]:{port}')

    return server
