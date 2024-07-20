from schemas.common import CommonModel


class CredentialsModel(CommonModel):
    '''Модель данных метода авторизации пользователя'''

    email: str
    password: str


class UpdateCredentialsModel(CommonModel):
    '''Модель данных метода изменения аутентификационных данных'''

    old_password: str
    new_password: str
