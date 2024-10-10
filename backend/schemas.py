from pydantic import BaseModel
from typing import Dict, Optional
from models import Role

# Модель для создания пользователя через API
class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "user"

    class Config:
        json_schema_extra = {
            "example": {
                "username": "new_user",
                "password": "strongpassword123",
                "role": "user"
            }
        }

# Модель для возврата данных пользователя через API
class UserResponse(BaseModel):
    username: str
    role: str
    is_active: bool

    class Config:
        from_attributes = True  # Поддержка ORM моделей SQLAlchemy
        json_schema_extra = {
            "example": {
                "username": "user-1",
                "role": "user",
                "is_active": True
            }
        }

# Модель данных для изменения контракта
class ContractChangeRequest(BaseModel):
    username: str  # Имя пользователя, чей контракт нужно изменить
    contract_data: Dict[str, str]  # Словарь с данными контракта

    class Config:
        json_schema_extra = {
            "example": {
                "username": "john_doe",
                "contract_data": {
                    "position": "Software Engineer",
                    "salary": "120000",
                    "contract_start": "2023-01-01",
                    "contract_end": "2024-01-01"
                }
            }
        }

# Модель для назначения роли пользователю (админом)
class RoleAssignmentRequest(BaseModel):
    username: str
    role: Role

    class Config:
        json_schema_extra = {
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
    username: Optional[str] = None