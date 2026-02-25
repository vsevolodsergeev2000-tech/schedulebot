from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, BigInteger, ForeignKey
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func
from config import settings

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String, nullable=True)
    timezone = Column(String, default="UTC")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    reminders = relationship("Reminder", back_populates="user", cascade="all, delete-orphan")

class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    chat_id = Column(BigInteger, nullable=False)
    text = Column(String, nullable=False)
    remind_time = Column(DateTime(timezone=True), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="reminders")

# Движок и фабрика сессий
engine = create_async_engine(settings.DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def init_db():
    """Создаёт таблицы при первом запуске (для простоты)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)