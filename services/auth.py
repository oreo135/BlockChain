from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from database import SessionLocal
from models import User
from fastapi.security import OAuth2PasswordBearer
import os

# JWT настройки
SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")
REFRESH_SECRET_KEY = os.getenv("REFRESH_SECRET_KEY", "your_refresh_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# OAuth2 схема
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Хэширование паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Создание токенов
def create_token(data: dict, secret_key: str, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=ALGORITHM)
    return encoded_jwt

def create_access_token(data: dict, expires_delta: timedelta = None):
    return create_token(data, SECRET_KEY, expires_delta)

def create_refresh_token(data: dict, expires_delta: timedelta = None):
    return create_token(data, REFRESH_SECRET_KEY, expires_delta)

# Получение текущего пользователя
def get_current_user(db: Session = Depends(SessionLocal), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Не удалось проверить учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user
