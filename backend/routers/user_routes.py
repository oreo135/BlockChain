import logging
import sys
import os
from fastapi.templating import Jinja2Templates
from sqlalchemy.sql import text
from fastapi.responses import HTMLResponse, RedirectResponse
from backend.utils.database import get_db
from fastapi import APIRouter, Depends, HTTPException, Request
from backend.models import Role, User
from backend.schemas import RoleAssignmentRequest, UserResponse
from backend.services.user_management import assign_role
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.services.auth import get_current_user


# Инициализация логирования
logger = logging.getLogger(__name__)

# Создание роутера
router = APIRouter()

templates = Jinja2Templates(directory="frontend/templates")

# Маршрут для получения всех пользователей
@router.get("/users/", response_model=list[UserResponse])
async def get_users(db: AsyncSession = Depends(get_db)):
    """
    Возвращает список всех пользователей в базе данных.

    :param db: Асинхронная сессия базы данных
    :return: Список пользователей в формате UserResponse
    """
    try:
        logger.info("Fetching all users from the database...")
        result = await db.execute(select(User))  # Выполняем запрос на выборку всех пользователей
        users = result.scalars().all()  # Получаем список пользователей из результата
        logger.info(f"Retrieved {len(users)} users.")
        return [
            UserResponse(
                username=user.username,
                role=user.role,
                is_active=user.is_active
            )
            for user in users
        ]
    except Exception as e:
        logger.error(f"Error while fetching users: {e}")
        raise HTTPException(status_code=500, detail="Ошибка получения списка пользователей")


# Маршрут для назначения ролей
@router.post("/assign_role/")
async def assign_role_endpoint(request: RoleAssignmentRequest, db: AsyncSession = Depends(get_db)):
    """
    Назначает роль пользователю. Только администраторы могут назначать роли.

    :param request: Объект RoleAssignmentRequest с информацией о пользователе и новой роли
    :param db: Асинхронная сессия базы данных
    :return: Сообщение о результате выполнения
    """
    try:
        logger.info(f"Assigning role '{request.role}' to user '{request.username}'...")

        # Проверяем, существует ли пользователь
        result = await db.execute(select(User).filter(User.username == request.username))
        user = result.scalars().first()

        if not user:
            logger.warning(f"User '{request.username}' not found.")
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        # Обновляем роль пользователя
        user.role = request.role
        await db.commit()  # Подтверждаем изменения
        logger.info(f"Role '{request.role}' assigned to user '{request.username}'.")
        return {"message": f"Role '{request.role}' assigned to user '{request.username}' successfully."}

    except Exception as e:
        logger.error(f"Error while assigning role: {e}")
        raise HTTPException(status_code=500, detail="Ошибка назначения роли")

@router.get("/profile", response_class=HTMLResponse)
async def profile_page(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if isinstance(current_user, RedirectResponse):
        return current_user

    all_users = await db.execute(text("SELECT username FROM users"))
    response = templates.TemplateResponse(
        "profile.html",
        {
            "request": request,
            "user": current_user,
            "all_users": all_users.fetchall(),
            "chat_history": []  # Заглушка для истории чата
        }
    )
    response.headers["Cache-Control"] = "no-store"  # Отключаем кэширование
    return response


