from schemas.common import CommonModel


class LogonHistoryModel(CommonModel):
    '''Модель данных метода получения историй авторизаций пользователя'''

    ip: str
    user_agent: str
    logon_time: str

    class Config:
        from_attributes = True
