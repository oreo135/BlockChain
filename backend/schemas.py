from typing import Dict, Optional
from datetime import datetime
from backend.models import Role
from pydantic import BaseModel, Field


# Модель для создания пользователя через API
class UserCreate(BaseModel):
    username: str = Field(..., description="Username of the user")
    password: str = Field(..., description="Password of the user")
    role: str = Field(default="user", description="Role assigned to the user")

    class Config:
        from_attributes = True  # Поддержка ORM моделей SQLAlchemy


class UserLogin(BaseModel):
    username: str = Field(..., description="Username of the user")
    password: str = Field(..., description="Password of the user")

    class Config:
        from_attributes = True


# Модель для возврата данных пользователя через API
class UserResponse(BaseModel):
    username: str = Field(..., description="Username of the user")
    role: str = Field(..., description="Role of the user")
    is_active: bool = Field(..., description="User's active status")

    class Config:
        from_attributes = True  # Поддержка ORM моделей SQLAlchemy

# Модель данных для изменения контракта
class ContractChangeRequest(BaseModel):
    username: str = Field(..., description="Username of the user whose contract needs to be changed")
    contract_data: Dict[str, str] = Field(..., description="Dictionary with contract data")

    class Config:
        from_attributes = True  # Поддержка ORM моделей SQLAlchemy

# Модель для назначения роли пользователю (админом)
class RoleAssignmentRequest(BaseModel):
    username: str = Field(..., description="Username of the user")
    role: Role = Field(..., description="Role to assign to the user")

    class Config:
        from_attributes = True  # Поддержка ORM моделей SQLAlchemy

# Модель для авторизации и возврата токена
class Token(BaseModel):
    access_token: str = Field(..., description="Access token")
    token_type: str = Field(..., description="Token type, e.g., 'bearer'")

# Модель для данных токена
class TokenData(BaseModel):
    username: Optional[str] = Field(None, description="Username associated with the token")

class MessageCreate(BaseModel):
    receiver_id: int
    content: str

class MessageResponse(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    content: str
    timestamp: datetime

    class Config:
        from_attributes = True