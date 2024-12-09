import os
from datetime import timedelta

import jwt
from backend.utils.database import get_db
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from backend.services.auth import create_access_token, get_current_user
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

class TokenRefreshRequest(BaseModel):
    refresh_token: str

@router.post("/refresh_token")
async def refresh_access_token(request: TokenRefreshRequest):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Не удалось проверить refresh токен",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            request.refresh_token,
            os.getenv("REFRESH_SECRET_KEY"),
            algorithms=["HS256"]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.JWTError:
        raise credentials_exception

    access_token_expires = timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30)))
    access_token = create_access_token(data={"sub": username}, expires_delta=access_token_expires)

    return {"access_token": access_token, "token_type": "bearer"}


# class AccessTokenRequest(BaseModel):
#     username: str
#
# @router.post("/generate_access_token")
# async def generate_access_token(request: AccessTokenRequest):
#     """
#     Эндпоинт для генерации access токена вручную.
#     """
#     # Настраиваем время жизни токена
#     access_token_expires = timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30)))
#
#     # Генерация токена
#     access_token = create_access_token(
#         data={"sub": request.username},
#         expires_delta=access_token_expires
#     )
#
#     return {"access_token": access_token, "token_type": "bearer"}