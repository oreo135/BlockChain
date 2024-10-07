import os
import sys
from datetime import timedelta
from typing import List, Any
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from dotenv import load_dotenv

# Модули проекта
from models import User, Role, Base
from schemas import UserCreate, UserResponse, ContractChangeRequest, RoleAssignmentRequest
from database import SessionLocal, engine, get_db
from services.auth import oauth2_scheme, create_access_token, create_refresh_token, get_current_user
from services.user_management import assign_role, register_user
from controllers import users, contracts, voting, chat
import blockchain.blockchain_func as _blockchain

# Добавляем путь к директории backend
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Загружаем переменные окружения из .env
load_dotenv()

# Инициализация блокчейна и FastAPI
blockchain = _blockchain.Blockchain()

# Создание приложения FastAPI с lifespan для создания администратора при старте
@asynccontextmanager
async def lifespan(app: FastAPI):
    db_session = SessionLocal()
    try:
        admin_user = db_session.query(User).filter(User.username == "admin").first()
        if not admin_user:
            admin = User(
                username="admin",
                hashed_password=create_access_token({"sub": "admin"}),
                role=Role.ADMIN.value  # Устанавливаем роль администратора
            )
            db_session.add(admin)
            db_session.commit()
            print("Admin user created")
        else:
            print("Admin user already exists")
    finally:
        db_session.close()
    yield

app = FastAPI(lifespan=lifespan)

# Подключение статических файлов и шаблонов
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
static_directory = os.path.join(BASE_DIR, "../frontend/static")
templates_directory = os.path.join(BASE_DIR, "../frontend/templates")
app.mount("/static", StaticFiles(directory=static_directory), name="static")
templates = Jinja2Templates(directory=templates_directory)

# Создание таблиц при старте приложения
Base.metadata.create_all(bind=engine)


# Маршрут для обновления токена
@app.post("/refresh_token")
async def refresh_access_token(refresh_token: str):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Не удалось проверить refresh токен",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(refresh_token, os.getenv("REFRESH_SECRET_KEY"), algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    access_token_expires = timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30)))
    access_token = create_access_token(data={"sub": username}, expires_delta=access_token_expires)

    return {"access_token": access_token, "token_type": "bearer"}

# Регистрация нового пользователя
@app.post("/register/", response_model=UserResponse)
async def register_user_endpoint(user: UserCreate, db: Session = Depends(get_db)):
    return register_user(user=user, db=db)

# Авторизация (получение JWT токенов)
@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Неправильное имя пользователя или пароль")

    access_token_expires = timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30)))
    refresh_token_expires = timedelta(days=int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7)))

    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    refresh_token = create_refresh_token(data={"sub": user.username}, expires_delta=refresh_token_expires)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "redirect_url": "/dashboard" if user.role != Role.ADMIN.value else "/admin_dashboard"
    }

# Главная страница
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    username = request.cookies.get("username")
    if not username:
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse("index.html", {"request": request, "username": username})

# Логин
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# Логаут и удаление куки
@app.post("/logout")
async def logout_user(request: Request):
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("username")
    return response

# Защищенная страница (/dashboard)
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    username = request.cookies.get("username")
    if not username:
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse("dashboard.html", {"request": request, "username": username})

# Назначение ролей пользователям (только для админа)
@app.post("/assign_role/")
async def assign_role_endpoint(request: RoleAssignmentRequest, db: Session = Depends(get_db),
                               admin_user: User = Depends(get_current_user)):
    if admin_user.role != Role.ADMIN.value:
        raise HTTPException(status_code=403, detail="Только администратор может назначать роли")

    return assign_role(request=request, db=db)

# Маршрут для получения всех пользователей (только для админа)
@app.get("/users/", response_model=List[UserResponse])
async def get_users(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != Role.ADMIN.value:
        raise HTTPException(status_code=403, detail="Доступ запрещён: Только администраторы могут просматривать данные.")

    users = db.query(User).all()
    return [
        UserResponse(username=user.username, role=user.role, contract_active=user.contract_active,
                     last_update=user.last_update.isoformat())
        for user in users
    ]

# WebSocket для общения
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Сообщение: {data}")
    except WebSocketDisconnect:
        pass

# Маршрут для изменения контракта
@app.post("/add_contract_change/")
def add_contract_change(request: ContractChangeRequest, requesting_user: User = Depends(get_current_user),
                        db: Session = Depends(get_db)):
    user = blockchain.get_user(request.username)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    blockchain.add_contract_change(user, request.contract_data)
    return {"message": "Изменение контракта добавлено в блокчейн"}

# Маршрут для логирования доступа к данным
@app.post("/log_data_access/")
def log_data_access(username: str, key: str, requesting_user: User = Depends(get_current_user)):
    target_user = blockchain.get_user(username)
    if not target_user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    if not blockchain.check_access(requesting_user, key):
        raise HTTPException(status_code=403, detail="Доступ запрещён")

    blockchain.log_data_access(requesting_user, target_user, key)
    return {"message": "Доступ к данным записан в блокчейн"}

# Маршрут для создания голосования
@app.post("/create_vote/")
def create_vote(issue: str, votes: dict, requesting_user: User = Depends(get_current_user)):
    if requesting_user.role != Role.ADMIN:
        raise HTTPException(status_code=403, detail="Только администраторы могут создавать голосования")

    blockchain.create_vote(issue, votes)
    return {"message": "Голосование добавлено в блокчейн"}

# Маршрут для закрытия голосования
@app.post("/close_vote/")
def close_vote(issue: str, requesting_user: User = Depends(get_current_user)):
    if requesting_user.role != Role.ADMIN:
        raise HTTPException(status_code=403, detail="Только администраторы могут закрывать голосования")

    results = blockchain.get_vote_results(issue)
    if not results:
        raise HTTPException(status_code=404, detail="Голосование не найдено или уже закрыто")

    blockchain.close_vote(issue)
    return {"message": f"Голосование по вопросу '{issue}' закрыто", "results": results}

# Маршрут для получения данных пользователя
@app.get("/user_data/{username}/{key}")
def get_user_data(username: str, key: str, requesting_user: User = Depends(get_current_user)):
    user = blockchain.get_user(username)
    if not user or not blockchain.check_access(requesting_user, key):
        raise HTTPException(status_code=403, detail="Доступ запрещён")
    return {"data": user.get_data(key)}

# Маршрут для майнинга блока
@app.post("/mine_block/")
def mine_block(data: str):
    if not blockchain.is_chain_valid():
        raise HTTPException(status_code=400, detail="Блокчейн недействителен")
    block = blockchain.mine_block(data=data)
    return block
