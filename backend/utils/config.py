import os
from datetime import timedelta

from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()


class Settings:
    # Основные ключи
    SECRET_KEY: str = os.getenv("SECRET_KEY", "default_secret_key")
    REFRESH_SECRET_KEY: str = os.getenv("REFRESH_SECRET_KEY", "default_refresh_secret_key")
    ALGORITHM = "HS256"

    # Настройки базы данных
    DB_USER: str = os.getenv("DB_USER", "default_user")
    DB_PASS: str = os.getenv("DB_PASS", "default_password")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DB_NAME: str = os.getenv("DB_NAME", "default_db")
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    # JWT настройки
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))

    # Вспомогательные свойства
    @property
    def access_token_expire_delta(self) -> timedelta:
        return timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)

    @property
    def refresh_token_expire_delta(self) -> timedelta:
        return timedelta(days=self.REFRESH_TOKEN_EXPIRE_DAYS)


settings = Settings()
