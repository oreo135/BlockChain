import datetime as dt
from datetime import timezone
from enum import Enum

from sqlalchemy.sql import func
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import as_declarative

from backend.utils.database import Base




# Роли пользователей
class Role(str, Enum):
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"
    NONE = "none"


# Модель пользователя в базе данных (SQLAlchemy)
class User(Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}  # Используется, если модифицируешь существующую таблицу

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)  # Сделаем username обязательным
    hashed_password = Column(String, nullable=False)  # Пароль тоже должен быть обязательным
    role = Column(String, default=Role.NONE.value)
    position = Column(String, default="Employee")  # Поле "position"
    contract_active = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    last_update = Column(DateTime, default=lambda: dt.datetime.now(timezone.utc), onupdate=lambda: dt.datetime.now(timezone.utc))

    sent_messages = relationship("Message", foreign_keys="Message.sender_id", back_populates="sender")
    received_messages = relationship("Message", foreign_keys="Message.receiver_id", back_populates="receiver")

    # def __init__(self, username: str, hashed_password: str, role: str = Role.NONE.value,
    #              position: str = "Employee", contract_active: bool = True, is_active: bool = True):
    #     self.username = username
    #     self.hashed_password = hashed_password
    #     self.role = role
    #     self.position = position
    #     self.contract_active = contract_active
    #     self.is_active = is_active
    #     self.last_update = dt.datetime.now(timezone.utc)

    def assign_role(self, role: Role):
        """Назначить роль пользователю"""
        self.role = role.value
        self.last_update = dt.datetime.now(timezone.utc)

    def has_role(self, role: Role) -> bool:
        """Проверить, имеет ли пользователь заданную роль"""
        return self.role == role.value

    def update_contract_status(self, status: bool):
        """Обновить статус контракта"""
        self.contract_active = status
        self.last_update = dt.datetime.now(timezone.utc)


class Message(Base):
    __tablename__ = "messages"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_messages")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="received_messages")
