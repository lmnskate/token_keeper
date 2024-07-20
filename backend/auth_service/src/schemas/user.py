from pydantic import AliasChoices, Field
from schemas.common import CommonModel


class LocalUserCreateModel(CommonModel):
    '''Модель данных метода создания пользователя'''

    email: str
    password: str
    first_name: str
    last_name: str


class LocalUserAuthorizeModel(CommonModel):
    '''Модель данных метода авторизации пользователя'''

    email: str
    password: str


class ChangePasswordModel(CommonModel):
    '''Модель данных метода авторизации пользователя'''

    old_password: str
    new_password: str


class UserOauthModel(CommonModel):
    '''Модель для создания пользователя через OAuth'''

    id: str  # id пользователя, предоставляемое внешним сервисом
    email: str = Field(validation_alias=AliasChoices('email', 'default_email'))
    first_name: str = Field(validation_alias=AliasChoices('first_name', 'given_name'))
    last_name: str = Field(validation_alias=AliasChoices('last_name', 'family_name'))
