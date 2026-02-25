from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User as TgUser
from sqlalchemy import select
from db import AsyncSessionLocal, User

class UserRegistrationMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        tg_user: TgUser = data.get("event_from_user")
        if tg_user:
            async with AsyncSessionLocal() as session:
                result = await session.execute(
                    select(User).where(User.telegram_id == tg_user.id)
                )
                user = result.scalar_one_or_none()
                if not user:
                    user = User(
                        telegram_id=tg_user.id,
                        username=tg_user.username,
                        timezone="UTC"
                    )
                    session.add(user)
                    await session.commit()
                    await session.refresh(user)
                data["db_user"] = user
        return await handler(event, data)