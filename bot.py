import asyncio
from aiogram import Bot, Dispatcher
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from config import TOKEN, ADMIN_ID
from database.db import async_main
from handlers import (
    start,
    admin_commands,
    sender,
    check_username,
    reels,

)

import config
from Server import start_web_server   # импортируем функцию из server.py

bot = Bot(token=config.TOKEN)
dp = Dispatcher()

async def main():
    # Запускаем web-сервер для Render
    asyncio.create_task(start_web_server())

    # Запускаем бота
    await dp.start_polling(bot)
    
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

async def main():
    await async_main()

    engine = create_async_engine(url='sqlite+aiosqlite:///db.sqlite3')
    async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

    bot = Bot(token=TOKEN)
    dp = Dispatcher()

    dp.include_routers(
        start.router,
        admin_commands.router,
        sender.router,
        check_username.router,
        reels.router,
    )

    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
