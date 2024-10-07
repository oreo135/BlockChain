from sqlalchemy.orm import Session
from fastapi import HTTPException, Depends
from passlib.context import CryptContext
from models import User, Role
from schemas import UserCreate, RoleAssignmentRequest
from database import get_db

# Создаем контекст для хэширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Регистрация нового пользователя
def register_user(user: UserCreate, db: Session):
    hashed_password = pwd_context.hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Назначение ролей пользователям (только для админа)
def assign_role(request: RoleAssignmentRequest, db: Session, admin_user: User):
    if admin_user.role != Role.ADMIN.value:
        raise HTTPException(status_code=403, detail="Только администратор может назначать роли")

    user = db.query(User).filter(User.username == request.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    user.role = request.role.value
    db.commit()

    return {"message": f"Роль {request.role} назначена пользователю {user.username}"}
