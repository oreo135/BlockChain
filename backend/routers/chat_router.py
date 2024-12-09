import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.models import User  # Модель User находится в models.py
from backend.utils.database import get_db  # Функция для получения сессии базы данных
from backend.schemas import MessageResponse, MessageCreate
from backend.services.auth import get_current_user
from backend.services.chat_service import create_message, get_messages_between_users
from backend.utils.database import Base
import logging
import inspect

logger = logging.getLogger(__name__)


# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

from sqlalchemy.orm import registry


@router.get("/users")
async def get_users(db: AsyncSession = Depends(get_db)):
    logger.info(f"User model file path: {inspect.getfile(User)}")


    try:
        try:
            async with db as session:
                logger.info("Successfully entered async with")
        except Exception as e:
            logger.error(f"Error in async with: {e}")
            raise HTTPException(status_code=500, detail="Failed to establish session.")

        logger.info(f"Using model: {User}")
        logger.info(f"User attributes: {dir(User)}")
        logger.info(f"User __tablename__: {getattr(User, '__tablename__', None)}")
        logger.info(f"User columns: {getattr(User, '__table__', None)}")

        # Явно указываем столбцы, чтобы исключить двусмысленность
        query = await session.execute(select(User.id, User.username))
        users = query.all()
        logger.info(f"Query successful, fetched users: {users}")
    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch users.")

    return [{"id": user_id, "username": username} for user_id, username in users]



@router.post("/send-message", response_model=MessageResponse)
async def send_message(
        message: MessageCreate,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
):
    logger.info(f"Attempting to send a message from user {current_user.id} to user {message.receiver_id}.")
    try:
        if message.receiver_id == current_user.id:
            logger.warning("User attempted to send a message to themselves.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot send a message to yourself."
            )
        new_message = await create_message(db, sender_id=current_user.id, message=message)
        logger.info(f"Message sent successfully: {new_message}")

        # Преобразование в Pydantic модель
        response = MessageResponse(
            id=new_message.id,
            sender_id=new_message.sender_id,
            receiver_id=new_message.receiver_id,
            content=new_message.content,
            timestamp=new_message.timestamp,
        )
        return response
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to send message.")


@router.get("/messages/{other_user_id}", response_model=list[MessageResponse])
async def get_message_history(
        other_user_id: int,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
):
    logger.info(f"Fetching message history between users {current_user.id} and {other_user_id}.")
    try:
        messages = await get_messages_between_users(db, current_user.id, other_user_id)
        logger.info(f"Message history fetched successfully: {messages}")
        return messages
    except Exception as e:
        logger.error(f"Error fetching message history: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch messages.")

