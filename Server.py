import os
import asyncio
from aiohttp import web

async def handle(request):
    return web.Response(text="Bot is running!")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle)
    port = int(os.getenv("PORT", 8080))  # Render передаёт порт в переменной окружения
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

# Для отладки (если хочешь запустить локально)
if __name__ == "__main__":
    asyncio.run(start_web_server())
