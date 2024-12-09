from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from backend.services.auth import get_current_user
from backend.models import User
import logging

# Инициализация шаблонов
templates = Jinja2Templates(directory="frontend/templates")

router = APIRouter()

logger = logging.getLogger(__name__)

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, current_user: User = Depends(get_current_user)):
    if isinstance(current_user, RedirectResponse):
        return current_user

    logger.info(f"User {current_user.username} with role {current_user.role} accessed dashboard")
    if current_user.role.lower() == "admin":
        logger.info("Rendering admin_dashboard.html")
        response = templates.TemplateResponse("admin_dashboard.html", {"request": request, "user": current_user})
    else:
        logger.info("Rendering dashboard.html")
        response = templates.TemplateResponse("dashboard.html", {"request": request, "user": current_user})

    # Добавляем заголовки для отключения кэша
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response