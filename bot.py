import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import TOKEN
from handlers import start, admin_commands, sender, check_username, reels
from Server import start_web_server  # функция без импорта bot/dispatcher

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

bot = Bot(token=TOKEN)
dp = Dispatcher()

dp.include_routers(
    start.router,
    admin_commands.router,
    sender.router,
    check_username.router,
    reels.router,
)

async def main():
    # Запуск веб-сервера с передачей bot и dp
    server_task = asyncio.create_task(start_web_server(bot, dp))

    # Запуск бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")
