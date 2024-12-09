from logging.config import fileConfig
from sqlalchemy import create_engine, pool
from alembic import context
import os
import logging
from backend.models import User, Message

# Alembic Config object, доступ к значению в alembic.ini
config = context.config

# Подключение логирования
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# MetaData ваших моделей (для autogenerate)
from backend.utils.database import Base

target_metadata = Base.metadata

print("=== Tables in Base.metadata ===")
print(target_metadata.tables.keys())
print("===============================")


# Получение строки подключения из alembic.ini или переменной окружения
DATABASE_URL = config.get_main_option("sqlalchemy.url")

# Если используется asyncpg в основном приложении, меняем на psycopg2 для миграций
if "asyncpg" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("asyncpg", "psycopg2")


def run_migrations_offline() -> None:
    """Запуск миграций в 'offline' режиме."""
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Запуск миграций в 'online' режиме."""
    connectable = create_engine(
        DATABASE_URL, poolclass=pool.NullPool
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


# Выбор режима миграций (offline/online)
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
