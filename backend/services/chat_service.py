from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from backend.models import Message
from backend.schemas import MessageCreate

async def create_message(db: AsyncSession, sender_id: int, message: MessageCreate):
    new_message = Message(
        sender_id=sender_id,
        receiver_id=message.receiver_id,
        content=message.content,
    )
    db.add(new_message)
    await db.commit()
    await db.refresh(new_message)
    return new_message

async def get_messages_between_users(db: AsyncSession, user_id: int, other_user_id: int):
    query = (
        select(Message)
        .where(
            ((Message.sender_id == user_id) & (Message.receiver_id == other_user_id))
            | ((Message.sender_id == other_user_id) & (Message.receiver_id == user_id))
        )
        .order_by(Message.timestamp)
        .options(joinedload(Message.sender), joinedload(Message.receiver))
    )
    result = await db.execute(query)
    return result.scalars().all()