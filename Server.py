from aiohttp import web
import asyncio
from aiogram.types import Update

async def handle_webhook(request):
    data = await request.json()
    update = Update(**data)  # конвертируем dict в Update
    await request.app["dp"].feed_update(update)  # передаем в Dispatcher
    return web.Response(text="OK")

async def start_web_server(bot, dp):
    """
    Запуск aiohttp веб-сервера для Render
    Биндится на 0.0.0.0:8000
    """
    app = web.Application()
    app["bot"] = bot
    app["dp"] = dp
    app.router.add_post("/webhook", handle_webhook)  # endpoint webhook

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8000)
    await site.start()

    print("Webhook server started on port 8000")
    while True:
        await asyncio.sleep(3600)  # держим сервер живым
