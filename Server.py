# Server.py
from aiohttp import web
import asyncio

async def handle(request):
    return web.Response(text="Bot is running!")

async def start_web_server():
    """
    Запускает aiohttp веб-сервер для Render.
    Биндится на 0.0.0.0:8000, чтобы Render видел открытый порт.
    """
    app = web.Application()
    app.router.add_get("/", handle)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8000)
    await site.start()

    # держим сервер живым в фоне
    while True:
        await asyncio.sleep(3600)
