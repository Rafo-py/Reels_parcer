from aiohttp import web
import asyncio
import json
from bot import dp, bot  # импортируем уже созданный Dispatcher и Bot

async def handle_webhook(request):
    try:
        data = await request.json()
        await dp.feed_update(data)  # правильно обрабатываем обновление
        return web.Response(status=200)
    except Exception as e:
        return web.Response(text=f"Error: {e}", status=500)

async def start_web_server():
    """
    Запускает aiohttp веб-сервер для Render.
    Биндится на 0.0.0.0:8000, чтобы Render видел открытый порт.
    """
    app = web.Application()
    app.router.add_post("/webhook", handle_webhook)  # путь, который Telegram будет дергать

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8000)
    await site.start()

    # держим сервер живым
    while True:
        await asyncio.sleep(3600)
