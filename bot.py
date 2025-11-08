# file: bot.py
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN, admin_group_id
from handlers import router as main_router

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Главная функция для запуска бота
async def main():
    # Проверка наличия обязательных переменных окружения
    if not BOT_TOKEN or not admin_group_id:
        logging.critical("!!! ОШИБКА: BOT_TOKEN или GROUP_ID не установлены в .env файле. Бот не может запуститься.")
        return

    # Инициализация бота и диспетчера
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()

    # Подключение главного роутера
    dp.include_router(main_router)

    logging.info("Бот запускается...")

    # Удаление старых вебхуков и запуск поллинга
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())