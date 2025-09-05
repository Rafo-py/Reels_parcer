from aiohttp import web
from aiogram import Bot, Dispatcher
import asyncio
from config import TOKEN, WEBHOOK_URL

bot = Bot(token=TOKEN)
dp = Dispatcher()


async def handle_webhook(request):
    data = await request.json()
    update = dp.update_class.model_validate(data, context={"bot": bot})
    asyncio.create_task(dp.feed_update(bot, update))
    return web.Response()


async def start_web_server():
    app = web.Application()
    app.router.add_post("/webhook", handle_webhook)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8000)
    await site.start()

    # Устанавливаем webhook в Telegram
    await bot.set_webhook(WEBHOOK_URL)

    print(f"Webhook set to {WEBHOOK_URL}")
    while True:
        await asyncio.sleep(3600)
