import asyncio

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text  # Импортируем text для текстовых SQL-запросов

DATABASE_URL = "postgresql+asyncpg://test_user:test_password@localhost/testdb"

engine = create_async_engine(DATABASE_URL, echo=True)

AsyncSessionLocal = sessionmaker(# type: ignore
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def test_connection():
    async with AsyncSessionLocal() as session:
        # Используем text для создания SQL-запроса
        result = await session.execute(text("SELECT 1"))
        print(result.scalar())

asyncio.run(test_connection())
