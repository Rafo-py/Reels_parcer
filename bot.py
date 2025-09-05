import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import TOKEN
from database.db import async_main
from handlers import start, admin_commands, sender, check_username, reels
from Server import start_web_server

# Логирование
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
        # Запускаем web-сервер (он и поставит webhook)
        server_task = asyncio.create_task(start_web_server())

        # Инициализация базы данных
        await async_main()

        logging.info("Бот запущен в режиме Webhook ✅")

        # держим сервер живым
        await server_task
    except Exception as e:
        logging.error(f"Ошибка при запуске бота или сервера: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
