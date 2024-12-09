import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import (AsyncEngine, AsyncSession,
                                    create_async_engine)
from sqlalchemy.orm import declarative_base, sessionmaker

# Загружаем переменные окружения из .env
load_dotenv()

# Читаем настройки из переменных окружения
DATABASE_URL = os.getenv("DATABASE_URL")

# Проверяем, указана ли переменная DATABASE_URL
if not DATABASE_URL:
    raise ValueError("Необходимо задать DATABASE_URL в файле .env")

# Преобразуем DATABASE_URL для асинхронного использования (asyncpg)
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# Создаем асинхронный движок SQLAlchemy
engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Установите True для отладки SQL-запросов
    future=True,
    pool_pre_ping=True  # Проверка соединения перед выполнением запроса
)

# Настраиваем асинхронную фабрику сессий
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Создаем базовый класс для моделей
Base = declarative_base()

# Функция для получения сессии базы данных
async def get_db():
    """
    Генератор для получения асинхронной сессии базы данных.
    Автоматически закрывает сессию после использования.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()
