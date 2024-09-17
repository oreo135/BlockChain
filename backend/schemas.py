from pydantic import BaseModel
from typing import Dict
from models import Role

class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "user"

class UserResponse(BaseModel):
    username: str
    role: str
    is_active: bool

    class Config:
        orm_mode = True

# Модель данных для изменения контракта
class ContractChangeRequest(BaseModel):
    username: str  # Имя пользователя, чей контракт нужно изменить
    contract_data: Dict[str, str]  # Словарь с данными контракта

    class Config:
        schema_extra = {
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