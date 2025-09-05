# bot.py
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher

# твой код бота тут
bot = Bot(token="TOKEN")
dp = Dispatcher()

async def handle(request):
    return web.Response(text="Bot is running!")

app = web.Application()
app.router.add_get("/", handle)

if __name__ == "__main__":
    import threading
    # Запуск aiohttp сервера, чтобы Render увидел порт
    threading.Thread(target=lambda: web.run_app(app, host="0.0.0.0", port=8000)).start()
    import asyncio
    asyncio.run(dp.start_polling(bot))
