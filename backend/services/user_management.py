from fastapi import HTTPException
from backend.models import Role, User
from passlib.context import CryptContext
from backend.schemas import RoleAssignmentRequest, UserCreate
from sqlalchemy.ext.asyncio import AsyncSession

# Создаем контекст для хэширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Тестирование хэширования и проверки
password = "my_secure_password"
hashed = pwd_context.hash(password)
print("Hashed password:", hashed)

assert pwd_context.verify(password, hashed), "Password verification failed"

# Асинхронная регистрация нового пользователя
async def register_user(user: UserCreate, db: AsyncSession):
    hashed_password = pwd_context.hash(user.password)
    await db.execute(
        text("INSERT INTO users (username, hashed_password, role, is_active) "
             "VALUES (:username, :hashed_password, :role, :is_active)"),
        {
            "username": user.username,
            "hashed_password": hashed_password,
            "role": "user",
            "is_active": True,
        }
    )
    await db.commit()

# Асинхронное назначение ролей пользователям (только для админа)
async def assign_role(request: RoleAssignmentRequest, db: AsyncSession, admin_user: User):
    """
    Асинхронная логика назначения роли пользователю.
    """
    if admin_user.role != Role.ADMIN.value:
        raise HTTPException(status_code=403, detail="Только администратор может назначать роли")

    result = await db.execute(text(
        f"SELECT * FROM users WHERE username='{request.username}'"))
    user = result.fetchone()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    await db.execute(
        text(f"UPDATE users SET role='{request.role.value}' WHERE username='{request.username}'")
    )
    await db.commit()

    return {"message": f"Роль {request.role} назначена пользователю {request.username}"}
