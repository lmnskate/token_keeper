import logging

from asgi_correlation_id.context import correlation_id
from logstash_async.handler import (AsynchronousLogstashHandler,
                                    LogstashFormatter)


class RequestIdFilter(logging.Filter):
    def filter(self, record):
        record.x_request_id = correlation_id.get()
        return True


def init_uvicorn_logger(
    host: str,
    port: int
) -> None:
    '''
    Функция инициализации логирования API с помощью Logstash

    :param host: хост сервера Logstash
    :param port: порт сервера Logstash
    '''

    logger = logging.getLogger(
        name='uvicorn.access'
    )

    handler = AsynchronousLogstashHandler(
        host=host,
        port=port,
        database_path='logstash.db',
    )

    handler.setFormatter(
        fmt=LogstashFormatter(tags=['ugc_uvicorn'])
    )

    handler.addFilter(
        filter=RequestIdFilter()
    )

    logger.addHandler(
        hdlr=handler
    )
