from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from backend.services.auth import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession
from backend.utils.database import get_db

# class AddUserMiddleware(BaseHTTPMiddleware):
#     async def dispatch(self, request: Request, call_next):
#         # Инициализация request.state.user как None
#         request.state.user = None
#
#         # Проверяем наличие токена в cookies
#         access_token = request.cookies.get("access_token")
#         if access_token:
#             try:
#                 # Создаем сессию базы данных
#                 async with get_db() as db:
#                     # Пытаемся получить текущего пользователя
#                     request.state.user = await get_current_user(request, db)
#             except Exception as e:
#                 # В случае ошибки оставляем пользователя как None
#                 print(f"Error in middleware: {e}")
#                 request.state.user = None
#
#         # Передаем управление следующему middleware или обработчику
#         response = await call_next(request)
#         return response

class NoCacheMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        print('кэш очищен')
        return response