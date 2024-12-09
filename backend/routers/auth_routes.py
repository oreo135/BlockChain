from datetime import timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from backend.schemas import UserLogin, RoleAssignmentRequest, UserCreate, UserResponse
from backend.utils.database import get_db
from backend.services.auth import (
    create_access_token,
    create_refresh_token,
    get_current_user
)
from backend.services.user_management import assign_role
from backend.models import User
from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext
from starlette.responses import RedirectResponse

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Регистрация нового пользователя
@router.post("/register", response_model=UserResponse)
async def register_user_route(user: UserCreate, db: AsyncSession = Depends(get_db)):
    # Проверка, существует ли пользователь
    existing_user = await db.execute(
        text("SELECT * FROM users WHERE username = :username"),
        {"username": user.username},
    )
    if existing_user.fetchone():
        raise HTTPException(status_code=400, detail="User already exists")

    # Устанавливаем роль по умолчанию: "user"
    hashed_password = pwd_context.hash(user.password)
    await db.execute(
        text(
            "INSERT INTO users (username, hashed_password, role, is_active) "
            "VALUES (:username, :hashed_password, :role, :is_active)"
        ),
        {
            "username": user.username,
            "hashed_password": hashed_password,
            "role": "user",  # Роль по умолчанию
            "is_active": True,
        },
    )
    await db.commit()

    return UserResponse(
        username=user.username,
        role="user",  # Отправляем информацию о роли "user"
        is_active=True,
    )


# Авторизация и получение токенов через стандартный OAuth2
@router.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    # Поиск пользователя в базе данных
    result = await db.execute(
        text("SELECT * FROM users WHERE username = :username"),
        {"username": form_data.username},
    )
    user = result.fetchone()

    # Проверка пароля
    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Создание токенов
    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


# Авторизация через кастомный маршрут
@router.post("/login")
async def login(
    request: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    username = request.username
    password = request.password

    # Поиск пользователя
    result = await db.execute(
        text("SELECT * FROM users WHERE username = :username"),
        {"username": username},
    )
    user = result.fetchone()

    # Проверка пароля
    if not user or not pwd_context.verify(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Создание токенов
    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})

    # Возвращаем токены в куках
    response = JSONResponse({"message": "Login successful"})
    response.set_cookie(key="access_token", value=access_token, httponly=True, max_age=3600)
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, max_age=7 * 24 * 3600)

    return response

# Назначение ролей пользователю (только администратор)
@router.post("/assign_role/")
async def assign_role_route(
    request: RoleAssignmentRequest,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(get_current_user)
):
    return await assign_role(request, db, admin_user)


@router.get("/logout", tags=["auth"])
async def logout(response: Response):
    # Создаем RedirectResponse
    redirect_response = RedirectResponse(url="/login", status_code=302)

    # Удаляем cookies, добавляя соответствующие заголовки в RedirectResponse
    redirect_response.delete_cookie("access_token", path="/")
    redirect_response.delete_cookie("refresh_token", path="/")

    # Добавляем заголовки для отключения кэша
    redirect_response.headers["Cache-Control"] = "no-store"
    redirect_response.headers["Pragma"] = "no-cache"
    redirect_response.headers["Expires"] = "0"

    print("Logout executed. Cookies deleted.")
    return redirect_response
