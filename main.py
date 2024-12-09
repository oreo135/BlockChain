import logging
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from passlib.context import CryptContext
from sqlalchemy import text
from sqlalchemy.orm import clear_mappers
from backend.utils.database import AsyncSessionLocal, Base
from backend.models import Role, User


from backend.routers import (
    admin_routes,
    auth_routes,
    blockchain_routes,
    dashboard_routes,
    token_routes,
    user_routes,
    websocket_routes,
    chat_router,
)

# Настройка логирования
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Настройка путей
BASE_DIR = Path(__file__).resolve().parent
static_directory = BASE_DIR / "frontend" / "static"
templates_directory = BASE_DIR / "frontend" / "templates"

# Проверка директорий
if not static_directory.exists() or not templates_directory.exists():
    logger.error("Проверьте наличие директорий static и templates")
    raise RuntimeError("Проверьте наличие директорий static и templates")

# Lifespan для инициализации администратора
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@asynccontextmanager
async def lifespan(app: FastAPI):

    async with AsyncSessionLocal() as db_session:
        # Проверяем, существует ли администратор
        admin_user = await db_session.execute(
            text("SELECT * FROM users WHERE role = :role"), {"role": Role.ADMIN.value}
        )
        admin_user = admin_user.fetchone()
        if not admin_user:
            hashed_password = pwd_context.hash("admin")
            await db_session.execute(
                text("INSERT INTO users (username, hashed_password, role) VALUES (:username, :password, :role)"),
                {"username": "admin", "password": hashed_password, "role": Role.ADMIN.value},
            )
            await db_session.commit()
            logger.info("Admin user created")
        else:
            logger.info("Admin user already exists")
    yield


# Создание приложения


app = FastAPI(lifespan=lifespan)

# Подключение статических файлов и шаблонов
app.mount("/static", StaticFiles(directory=static_directory), name="static")
templates = Jinja2Templates(directory=str(templates_directory))

logger.info(f"Static directory being mounted: {static_directory}")
logger.debug(f"Static directory contents: {list(static_directory.iterdir())}")

# Подключение роутеров


app.include_router(chat_router.router, prefix="/api/chat", tags=["Chat"])
app.include_router(auth_routes.router, prefix="/auth", tags=["auth"])
app.include_router(admin_routes.router, prefix="/admin", tags=["admin"])
app.include_router(blockchain_routes.router, prefix="/blockchain", tags=["blockchain"])
app.include_router(websocket_routes.router, tags=["websocket"])
app.include_router(token_routes.router, prefix="/token", tags=["token"])
app.include_router(dashboard_routes.router, tags=["dashboard"])
app.include_router(user_routes.router, prefix="/user", tags=["user"])

# Маршруты для отображения страниц
@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    logger.info("Rendering home page")
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    logger.info("Rendering login page")
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    logger.info("Rendering register page")
    return templates.TemplateResponse("register.html", {"request": request})


# Защищенный маршрут
@app.get("/protected")
async def protected_route():
    return {"message": "This is a protected route"}
