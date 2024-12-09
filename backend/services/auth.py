import logging
from datetime import datetime, timedelta, timezone
from fastapi.responses import RedirectResponse

from sqlalchemy.sql import text
from backend.utils.config import settings
from backend.utils.database import get_db
from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from backend.models import User
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional


# Настройка логирования
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# OAuth2 схема
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# Хэширование паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Функция для создания токена
def create_token(data: dict, secret_key: str, expires_delta: timedelta) -> str:
    """
    Создаёт JWT токен с заданными данными, секретным ключом и временем жизни.

    :param data: Данные для включения в токен
    :param secret_key: Секретный ключ для подписи токена
    :param expires_delta: Время жизни токена
    :return: Закодированный JWT токен
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta  # Используем timezone-aware datetime
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, secret_key, algorithm=settings.ALGORITHM)



def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    return create_token(data, settings.SECRET_KEY, expires_delta
                        or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))

def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    return create_token(data, settings.REFRESH_SECRET_KEY, expires_delta
                        or timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))

from fastapi.responses import RedirectResponse

async def get_current_user(
    request: Request, db: AsyncSession = Depends(get_db)
) -> User:
    # Получение токена из cookies
    access_token = request.cookies.get("access_token")
    print(f"Access Token: {access_token}")
    if not access_token:
        print("Access Token missing. Redirecting to login.")
        return RedirectResponse(url="/login", status_code=302)

    try:
        # Декодируем токен, используя секретный ключ и алгоритм
        payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username = payload.get("sub")  # Получаем username из токена
        print(f"Decoded Username: {username}")
        if not username:
            print("Invalid Token: No username.")
            return RedirectResponse(url="/login", status_code=302)
    except JWTError:
        print("Invalid Token: Decoding failed.")
        return RedirectResponse(url="/login")

    # Выполняем запрос к базе данных, чтобы найти пользователя
    result = await db.execute(
        text("SELECT * FROM users WHERE username = :username"),
        {"username": username},
    )
    user = result.fetchone()
    print(f"Fetched User: {user}")
    if user is None:
        print("User not found in database.")
        return RedirectResponse(url="/login", status_code=302)

    return user
