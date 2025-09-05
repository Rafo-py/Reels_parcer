from aiohttp import web
import asyncio

async def handle_webhook(request, dp, bot):
    data = await request.json()
    await dp.feed_update(data)  # обработка обновления
    return web.Response(status=200)

async def start_web_server(bot, dp):
    app = web.Application()
    # передаем dp и bot через lambda
    app.router.add_post("/webhook", lambda request: handle_webhook(request, dp, bot))

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8000)
    await site.start()

    while True:
        await asyncio.sleep(3600)
