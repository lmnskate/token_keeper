import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from werkzeug.security import check_password_hash, generate_password_hash

from dependencies.postgres import Base


class User(Base):
    '''Модель сущности пользователя'''

    __tablename__ = 'users'

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False
    )
    email = Column(
        String(255),
        unique=True,
        nullable=False
    )
    password = Column(
        String(255),
        nullable=False
    )
    first_name = Column(String(50))
    last_name = Column(String(50))
    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    logon_histories = relationship(
        'LogonHistory',
        back_populates='user'
    )

    def __init__(
        self,
        email: str,
        password: str,
        first_name: str,
        last_name: str
    ) -> None:
        self.email = email
        self.password = generate_password_hash(password)
        self.first_name = first_name
        self.last_name = last_name

    def set_updated_password(
        self,
        new_password: str
    ):
        self.password = generate_password_hash(new_password)

    def check_password(
        self,
        password: str
    ) -> bool:
        return check_password_hash(self.password, password)

    def __repr__(self) -> str:
        return f'<User {self.login}>'


class LogonHistory(Base):
    '''Модель сущности истории авторизаций пользователя'''

    __tablename__ = 'logon_histories'

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False
    )
    ip = Column(String(16))
    user_agent = Column(String(255))
    logon_time = Column(
        DateTime,
        default=datetime.utcnow())
    created_at = Column(
        DateTime,
        default=datetime.utcnow()
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey('users.id')
    )
    user = relationship(
        'User',
        back_populates='logon_histories'
    )

    def __init__(
        self,
        ip: str,
        user_agent: str,
        user_id: UUID
    ) -> None:
        self.ip = ip
        self.user_agent = user_agent
        self.user_id = user_id

    def __repr__(self) -> str:
        return f'<Logon history for user {self.user_id}>'
