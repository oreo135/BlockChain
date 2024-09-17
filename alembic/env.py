import os
import sys
from logging.config import fileConfig
from sqlalchemy import create_engine
from sqlalchemy import pool
from alembic import context
from dotenv import load_dotenv

# Добавляем путь к директории backend
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Загружаем переменные окружения
load_dotenv()

# Импортируем базу данных и модели
from backend.database import Base  # Корректный импорт базы данных
from backend import models  # Импорт всех моделей через пакет

# Настройка конфигурации Alembic
config = context.config
fileConfig(config.config_file_name)

# Подключаем метаданные моделей для создания таблиц
target_metadata = Base.metadata

# Получаем URL базы данных из переменных окружения
database_url = os.getenv("DATABASE_URL")

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    context.configure(
        url=database_url,  # Используем переменную окружения для подключения к базе данных
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = create_engine(  # Используем create_engine напрямую для online режима
        database_url,  # Используем переменную окружения для подключения к базе данных
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
