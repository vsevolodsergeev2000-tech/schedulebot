import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from config import settings
from db import init_db
from middlewares import UserRegistrationMiddleware
from handlers import router
from scheduler import scheduler, restore_reminders

logging.basicConfig(level=logging.INFO)

async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="remind", description="Создать напоминание"),
        BotCommand(command="list", description="Список напоминаний"),
        BotCommand(command="cancel", description="Отменить напоминание"),
    ]
    await bot.set_my_commands(commands)

async def main():
    # Инициализация БД
    await init_db()

    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()

    # Подключаем middleware
    dp.message.middleware(UserRegistrationMiddleware())

    # Подключаем обработчики
    dp.include_router(router)

    # Устанавливаем команды меню
    await set_commands(bot)

    # Восстанавливаем активные напоминания в планировщик
    await restore_reminders(bot)

    # Запускаем планировщик
    scheduler.start()

    # Запускаем бота
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())