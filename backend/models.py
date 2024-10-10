from enum import Enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime
import datetime as dt
from database import Base

# Роли пользователей
class Role(str, Enum):
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"
    NONE = "none"

# Модель пользователя в базе данных (SQLAlchemy)
class User(Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}  # Добавляем это, если нужно изменить уже существующую таблицу

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default=Role.NONE.value)
    contract_active = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    last_update = Column(DateTime, default=dt.datetime.utcnow)

    def __init__(self, username: str, hashed_password: str, role: str = Role.NONE.value,
                 contract_active: bool = True, is_active: bool = True):
        self.username = username
        self.hashed_password = hashed_password
        self.role = role
        self.contract_active = contract_active
        self.is_active = is_active
        self.last_update = dt.datetime.now(dt.timezone.utc)  # Используем временную зону

    def assign_role(self, role: Role):
        self.role = role.value
        self.last_update = dt.datetime.now(dt.timezone.utc)  # Используем временную зону

    def has_role(self, role: Role) -> bool:
        return self.role == role.value

    def update_contract_status(self, status: bool):
        self.contract_active = status
        self.last_update = dt.datetime.now(dt.timezone.utc)