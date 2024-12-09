from backend.utils.database import get_db
from fastapi import APIRouter, Depends, HTTPException
from backend.models import Role, User
from backend.schemas import RoleAssignmentRequest, UserResponse
from backend.services.auth import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

# Получение всех пользователей (только администратор)
@router.get("/users", response_model=list[UserResponse])
async def get_all_users(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != Role.ADMIN.value:
        raise HTTPException(status_code=403, detail="Access denied")
    users = await db.execute(text("SELECT * FROM users"))
    return [UserResponse(username=u.username, role=u.role, is_active=u.is_active) for u in users.fetchall()]
