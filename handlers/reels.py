from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ParseMode
import re
import asyncio
from functools import partial

from config import TOKEN
from parse_reels import fetch_top_reels_public  # новый парсер

router = Router()
router.message.filter(F.chat.type == "private")

bot = Bot(token=TOKEN)

USERNAME_RE = re.compile(r"^[a-zA-Z0-9._]{1,30}$")

@router.message(Command("reels"))
async def cmd_reels(message: Message):
    """
    Usage examples:
      /reels nasa                 -> top 5 reels by virality
      /reels nasa 10              -> top 10
      /reels nasa 10 0.5          -> top 10 with min_ratio 0.5
    """
    parts = (message.text or "").split()
    if len(parts) < 2:
        await message.answer("Укажи username: <code>/reels username [limit] [min_ratio]</code>", parse_mode=ParseMode.HTML)
        return

    username = parts[1].strip().lstrip("@")
    if not USERNAME_RE.match(username):
        await message.answer("⚠️ Некорректный username.")
        return

    limit = 5
    min_ratio = 0.0
    if len(parts) >= 3:
        try:
            limit = max(1, min(50, int(parts[2])))
        except:
            pass
    if len(parts) >= 4:
        try:
            min_ratio = max(0.0, float(parts[3]))
        except:
            pass

    waiting = await message.answer("🔎 Ищу вирусные Reels…")

    try:
        followers, reels, is_private = await _fetch_reels_async(username, limit, min_ratio)
    except Exception as e:
        await waiting.edit_text("❌ Ошибка при получении Reels. Возможно, аккаунт не существует или закрыт.")
        return

    if is_private:
        await waiting.edit_text(f"⚠️ Аккаунт @{username} закрыт. Парсинг невозможен.")
        return

    if not reels:
        await waiting.edit_text("🤷‍♂️ Ничего не нашёл по заданным условиям.")
        return

    lines = [f"📊 Топ Reels @{username} (подписчики: {followers:,})".replace(",", " ")]
    for i, (url, views, ratio) in enumerate(reels, 1):
        lines.append(f"{i}. {url} — 👀 {views:,} • 🤩 вирусность {ratio:.2f}".replace(",", " "))
    await waiting.edit_text("\n".join(lines))


async def _fetch_reels_async(username: str, limit: int, min_ratio: float):
    """
    Запуск блокирующего instaloader в отдельном потоке
    """
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        None,
        partial(fetch_top_reels_public, username, limit, min_ratio)
    )
