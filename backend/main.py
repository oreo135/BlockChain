import os
import sys
from sqlalchemy import text
from fastapi import FastAPI, Request, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from models import User, Role, Base
from schemas import UserCreate, UserResponse, ContractChangeRequest, RoleAssignmentRequest
from database import SessionLocal, engine
import blockchain as _blockchain
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import List
from dotenv import load_dotenv
from contextlib import asynccontextmanager

# Добавляем путь к директории backend
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Загружаем переменные окружения из .env
load_dotenv()

# Инициализация блокчейна, FastAPI, и базы данных
blockchain = _blockchain.Blockchain()

# JWT настройки
SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Хэширование паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Пути к статическим файлам и шаблонам
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Получаем базовую директорию, в которой находится main.py
static_directory = os.path.join(BASE_DIR, "../frontend/static")  # Корректный путь к static
templates_directory = os.path.join(BASE_DIR, "../frontend/templates")  # Корректный путь к templates

# Использование lifespan для создания администратора
@asynccontextmanager
async def lifespan(app: FastAPI):
    db_session = SessionLocal()
    admin_user = db_session.query(User).filter(User.username == "admin").first()

    if not admin_user:
        admin = User(username="admin", hashed_password=pwd_context.hash("adminpassword"))
        db_session.add(admin)
        db_session.commit()
        print("Admin user created")
    else:
        print("Admin user already exists")

    yield
    db_session.close()


# Создание приложения FastAPI с lifespan
app = FastAPI(lifespan=lifespan)

# Подключение статических файлов и шаблонов
app.mount("/static", StaticFiles(directory=static_directory), name="static")
templates = Jinja2Templates(directory=templates_directory)

# Создание таблиц при старте приложения (но с миграциями)
Base.metadata.create_all(bind=engine)


# Получение сессии базы данных
def get_db():
    db_session = SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()

# Маршрут для проверки подключения к базе данных
@app.get("/check-db/")
def check_db(db: Session = Depends(get_db)):
    try:
        # Пробуем выполнить простой запрос
        result = db.execute(text("SELECT 1")).scalar()
        return {"status": "connected", "result": result}
    except Exception as e:
        return {"status": "error", "details": str(e)}

# JWT токен создание
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Получение текущего пользователя по токену
def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user


# Регистрация нового пользователя и добавление в блокчейн
@app.post("/register/", response_model=UserResponse)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    hashed_password = pwd_context.hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Добавляем пользователя в блокчейн
    blockchain.add_user(db_user)

    return db_user


# Авторизация (получение JWT токена)
@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    # Проверяем роль пользователя
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)

    if user.role == Role.ADMIN.value:
        return {"access_token": access_token, "token_type": "bearer", "redirect_url": "/admin_dashboard"}

    return {"access_token": access_token, "token_type": "bearer", "redirect_url": "/dashboard"}


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


# Логин с обработкой JSON данных
@app.post("/login")
async def login_user(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    username = data.get("username")
    user = db.query(User).filter(User.username == username).first()
    if user:
        response = RedirectResponse(url="/", status_code=302)
        response.set_cookie(key="username", value=username)
        return response
    else:
        raise HTTPException(status_code=404, detail="User not found, please register")


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
async def assign_role(request: RoleAssignmentRequest, db: Session = Depends(get_db),
                      admin_user: User = Depends(get_current_user)):
    if admin_user.role != Role.ADMIN.value:
        raise HTTPException(status_code=403, detail="Only admins can assign roles")

    user = db.query(User).filter(User.username == request.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.role = request.role.value
    db.commit()

    blockchain_user = blockchain.get_user(user.username)
    blockchain_user.role = request.role.value

    return {"message": f"Role {request.role} assigned to {user.username}"}


# Маршрут для получения всех пользователей (только для админа)
@app.get("/users/", response_model=List[UserResponse])
async def get_users(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != Role.ADMIN.value:
        raise HTTPException(status_code=403, detail="Access forbidden: Only admins can access this data.")

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
            await websocket.send_text(f"Message text was: {data}")
    except WebSocketDisconnect:
        pass


# Маршрут для изменения контракта
@app.post("/add_contract_change/")
def add_contract_change(request: ContractChangeRequest, requesting_user: User = Depends(get_current_user),
                        db: Session = Depends(get_db)):
    user = blockchain.get_user(request.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    blockchain.add_contract_change(user, request.contract_data)
    return {"message": "Contract change added to blockchain"}


# Маршрут для логирования доступа к данным
@app.post("/log_data_access/")
def log_data_access(username: str, key: str, requesting_user: User = Depends(get_current_user)):
    target_user = blockchain.get_user(username)
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    if not blockchain.check_access(requesting_user, key):
        raise HTTPException(status_code=403, detail="Access denied")

    blockchain.log_data_access(requesting_user, target_user, key)
    return {"message": "Data access logged in blockchain"}


# Маршрут для создания голосования
@app.post("/create_vote/")
def create_vote(issue: str, votes: dict, requesting_user: User = Depends(get_current_user)):
    if requesting_user.role != Role.ADMIN:
        raise HTTPException(status_code=403, detail="Only admins can create votes")

    blockchain.create_vote(issue, votes)
    return {"message": "Vote added to blockchain"}


# Маршрут для закрытия голосования
@app.post("/close_vote/")
def close_vote(issue: str, requesting_user: User = Depends(get_current_user)):
    if requesting_user.role != Role.ADMIN:
        raise HTTPException(status_code=403, detail="Only admins can close votes")

    results = blockchain.get_vote_results(issue)
    if not results:
        raise HTTPException(status_code=404, detail="Vote not found or already closed")

    blockchain.close_vote(issue)
    return {"message": f"Vote on issue '{issue}' is closed.", "results": results}


# Маршрут для получения данных пользователя
@app.get("/user_data/{username}/{key}")
def get_user_data(username: str, key: str, requesting_user: User = Depends(get_current_user)):
    user = blockchain.get_user(username)
    if not user or not blockchain.check_access(requesting_user, key):
        raise HTTPException(status_code=403, detail="Access denied")
    return {"data": user.get_data(key)}


# Маршрут для майнинга блока
@app.post("/mine_block/")
def mine_block(data: str):
    if not blockchain.is_chain_valid():
        raise HTTPException(status_code=400, detail="The blockchain is invalid")
    block = blockchain.mine_block(data=data)
    return block
