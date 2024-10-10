from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# Читаем настройки из окружения
DATABASE_URL = os.getenv("DATABASE_URL")

# Проверка наличия DATABASE_URL
if not DATABASE_URL:
    raise ValueError("Необходимо задать DATABASE_URL в файле .env")

# Создаем движок и фабрику сессий
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Функция получения сессии базы данных
def get_db():
    db_session = SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()