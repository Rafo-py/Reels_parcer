import asyncio
import logging
from aiogram import Bot, Dispatcher
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from config import TOKEN, ADMIN_ID
from database.db import async_main
from handlers import start, admin_commands, sender, check_username, reels
from Server import start_web_server

# Логирование
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Подключаем роутеры
dp.include_routers(
    start.router,
    admin_commands.router,
    sender.router,
    check_username.router,
    reels.router,
)

async def main():
    try:
        # БД
        await async_main()
        engine = create_async_engine(url='sqlite+aiosqlite:///db.sqlite3')
        async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

        # Запуск веб-сервера + webhook
        await start_web_server()
    except Exception as e:
        logging.error(f"Ошибка при запуске бота или сервера: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
