from aiogram import Router, types
from aiogram.filters import Command
from sqlalchemy import select
from db import AsyncSessionLocal, Reminder
from scheduler import add_reminder_job, remove_reminder_job
from utils import parse_datetime
from config import settings
import pytz
from datetime import datetime
from utils import parse_moscow_to_utc, format_moscow_from_utc

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message, db_user):
    await message.answer(
        f"👋 Привет, {db_user.username or 'пользователь'}!\n"
        "/remind <текст> <ДД.ММ.ГГГГ ЧЧ:ММ> — создать напоминание (время UTC)\n"
        "/list — список активных напоминаний\n"
        "/cancel <номер> — отменить напоминание"
    )

@router.message(Command("remind"))
async def cmd_remind(message: types.Message, db_user, bot):
    args = message.text.split(maxsplit=2)
    if len(args) < 3:
        await message.answer("❌ Использование: /remind <текст> <ДД.ММ.ГГГГ ЧЧ:ММ> (время UTC)")
        return

    text = args[1]
    datetime_str = args[2]

    try:
        remind_time = parse_moscow_to_utc(datetime_str)
    except ValueError as e:
        await message.answer(f"❌ {e}")
        return

    if remind_time <= datetime.now(pytz.UTC):
        await message.answer("❌ Время напоминания должно быть в будущем.")
        return

    async with AsyncSessionLocal() as session:
        reminder = Reminder(
            user_id=db_user.id,
            chat_id=message.chat.id,
            text=text,
            remind_time=remind_time,
            is_active=True
        )
        session.add(reminder)
        await session.commit()
        await session.refresh(reminder)

    add_reminder_job(reminder.id, remind_time, message.chat.id, text, bot)

    await message.answer(
        f"✅ Напоминание установлено на {format_moscow_from_utc(remind_time)}\n"
        f"ID: {reminder.id}"
    )

@router.message(Command("list"))
async def cmd_list(message: types.Message, db_user):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Reminder)
            .where(Reminder.user_id == db_user.id, Reminder.is_active == True)
            .order_by(Reminder.remind_time)
        )
        reminders = result.scalars().all()

    if not reminders:
        await message.answer("📭 У вас нет активных напоминаний.")
        return

    lines = []
    for idx, rem in enumerate(reminders, 1):
        lines.append(f"{idx}. ID {rem.id}: {rem.text} — {format_moscow_from_utc(rem.remind_time)}")
    await message.answer("📋 Ваши активные напоминания:\n" + "\n".join(lines))

@router.message(Command("cancel"))
async def cmd_cancel(message: types.Message, db_user):
    args = message.text.split()
    if len(args) != 2:
        await message.answer("❌ Использование: /cancel <номер из списка /list>")
        return

    try:
        index = int(args[1]) - 1
    except ValueError:
        await message.answer("❌ Номер должен быть числом.")
        return

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Reminder)
            .where(Reminder.user_id == db_user.id, Reminder.is_active == True)
            .order_by(Reminder.remind_time)
        )
        reminders = result.scalars().all()

        if index < 0 or index >= len(reminders):
            await message.answer("❌ Напоминание с таким номером не найдено.")
            return

        reminder = reminders[index]
        reminder.is_active = False
        await session.commit()

    remove_reminder_job(reminder.id)

    await message.answer("✅ Напоминание отменено.")