# server.py
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher
from config import TOKEN  # ✅ используем реальный токен из env

# Создаём бота и диспетчер
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Простая проверка работы сервера
async def handle(request):
    return web.Response(text="Bot is running!")

# Создаём aiohttp приложение
app = web.Application()
app.router.add_get("/", handle)

# Функция для запуска web-сервера
def run_web_server():
    web.run_app(app, host="0.0.0.0", port=8000)

# Функция для запуска бота и веб-сервера вместе
async def start_web_server():
    loop = asyncio.get_event_loop()
    # Запускаем веб-сервер в отдельном потоке
    import threading
    threading.Thread(target=run_web_server, daemon=True).start()
    # Запускаем polling бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(start_web_server())
