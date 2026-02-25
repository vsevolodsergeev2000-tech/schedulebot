from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from datetime import datetime
from aiogram import Bot
from db import AsyncSessionLocal, Reminder
from sqlalchemy import select, update
from config import settings

scheduler = AsyncIOScheduler(timezone=settings.TIMEZONE)

async def send_reminder(reminder_id: int, chat_id: int, text: str, bot: Bot):
    """Отправляет напоминание и деактивирует его."""
    try:
        await bot.send_message(chat_id=chat_id, text=f"🔔 Напоминание: {text}")
    except Exception as e:
        print(f"Ошибка отправки напоминания {reminder_id}: {e}")
    finally:
        async with AsyncSessionLocal() as session:
            await session.execute(
                update(Reminder).where(Reminder.id == reminder_id).values(is_active=False)
            )
            await session.commit()

def add_reminder_job(reminder_id: int, remind_time: datetime, chat_id: int, text: str, bot: Bot):
    """Добавляет задание в планировщик."""
    scheduler.add_job(
        send_reminder,
        trigger=DateTrigger(run_date=remind_time),
        args=[reminder_id, chat_id, text, bot],
        id=f"reminder_{reminder_id}",
        replace_existing=True,
    )

def remove_reminder_job(reminder_id: int):
    """Удаляет задание из планировщика."""
    job_id = f"reminder_{reminder_id}"
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)

async def restore_reminders(bot: Bot):
    """Восстанавливает активные напоминания из БД при старте."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Reminder).where(Reminder.is_active == True)
        )
        reminders = result.scalars().all()
        for rem in reminders:
            if rem.remind_time <= datetime.now(rem.remind_time.tzinfo):
                rem.is_active = False
                await session.commit()
                continue
            add_reminder_job(rem.id, rem.remind_time, rem.chat_id, rem.text, bot)