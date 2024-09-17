import sys
import os
from enum import Enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field
import datetime as dt
from database import Base

# Добавляем путь к директории backend
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

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

    def __init__(self, username: str, hashed_password: str, contract_active: bool=True, is_active: bool=True):
        self.username = username
        self.hashed_password = hashed_password
        self.role = Role.NONE.value
        self.contract_active = contract_active
        self.is_active = is_active
        self.last_update = dt.datetime.utcnow()

    def assign_role(self, role: Role):
        self.role = role.value
        self.last_update = dt.datetime.utcnow()

    def has_role(self, role: Role) -> bool:
        return self.role == role.value

    def update_contract_status(self, status: bool):
        self.contract_active = status
        self.last_update = dt.datetime.utcnow()


# Pydantic модели для запросов и ответов

# Модель для создания пользователя через API
class UserCreate(BaseModel):
    username: str
    password: str  # Пользователь создается с паролем, но без роли

    class Config:
        schema_extra = {
            "example": {
                "username": "new_user",
                "password": "strongpassword123"
            }
        }


# Модель для возврата данных пользователя через API
class UserResponse(BaseModel):
    username: str
    role: Role
    contract_active: bool
    last_update: str

    class Config:
        orm_mode = True  # Поддержка ORM моделей SQLAlchemy
        schema_extra = {
            "example": {
                "username": "user-1",
                "role": "none",  # Роль по умолчанию после регистрации
                "contract_active": True,
                "last_update": "2024-09-05T12:00:00"
            }
        }


# Модель для назначения роли админом
class RoleAssignmentRequest(BaseModel):
    username: str
    role: Role

    class Config:
        schema_extra = {
            "example": {
                "username": "user-1",
                "role": "user"
            }
        }


# Модель для авторизации и возврата токена
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


# Модель для изменения контракта через API
class ContractChangeRequest(BaseModel):
    username: str
    contract_data: dict

    class Config:
        schema_extra = {
            "example": {
                "username": "user-1",
                "contract_data": {
                    "position": "Senior Developer",
                    "salary": 80000
                }
            }
        }
