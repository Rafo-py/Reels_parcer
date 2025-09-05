import asyncio
import logging
from aiogram import Bot, Dispatcher
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from config import TOKEN, ADMIN_ID
from database.db import async_main
from handlers import start, admin_commands, sender, check_username, reels
from Server import start_web_server  # импортируем функцию из server.py

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

# Создание бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Подключение роутеров
dp.include_routers(
    start.router,
    admin_commands.router,
    sender.router,
    check_username.router,
    reels.router,
)

async def main():
    try:
        # Запускаем web-сервер для Render в фоне
        server_task = asyncio.create_task(start_web_server())

        # Инициализация базы данных
        await async_main()
        engine = create_async_engine(url='sqlite+aiosqlite:///db.sqlite3')
        async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

        # Запуск бота
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"Ошибка при запуске бота или сервера: {e}")
    finally:
        await bot.session.close()  # корректное завершение сессии

if __name__ == '__main__':
    asyncio.run(main())
