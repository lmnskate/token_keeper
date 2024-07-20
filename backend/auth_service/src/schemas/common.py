from typing import Annotated

import orjson
from fastapi import Query
from pydantic import BaseModel


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class CommonModel(BaseModel):
    '''Общая модель'''

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class Paginator(BaseModel):
    '''Класс, содержащий настройки пагинации'''

    page_size: Annotated[int, Query(description='Размер страницы', ge=1)] = 10
    page_number: Annotated[int, Query(description='Номер страницы', ge=1)] = 1
