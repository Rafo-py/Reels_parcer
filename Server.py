# server.py
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher
from config import TOKEN

bot = Bot(token=TOKEN)
dp = Dispatcher()

async def handle(request):
    return web.Response(text="Bot is running!")

app = web.Application()
app.router.add_get("/", handle)

async def start_bot():
    await dp.start_polling(bot)

async def main():
    # Запускаем бота в фоне
    asyncio.create_task(start_bot())
    # Запускаем веб-сервер на порту 8000
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8000)
    await site.start()
    print("Server running on http://0.0.0.0:8000")
    # Бесконечно держим loop живым
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
