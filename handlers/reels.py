from aiogram import Router, types
from aiogram.filters import Command
from parse_reels import fetch_top_reels_public  # импортируем твою функцию

router = Router()

@router.message(Command("reels"))
async def get_reels(message: types.Message):
    """
    Обработчик команды /reels <username>
    Парсит публичный Instagram аккаунт и возвращает топ Reels.
    """
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Использование: /reels <username>")
        return

    username = args[1]

    await message.answer(f"Ищу Reels у пользователя: {username}… ⏳")

    try:
        followers, reels, is_private = fetch_top_reels_public(username, limit=5, min_ratio=0.01)
    except ValueError as e:
        await message.answer(f"Ошибка: {e}")
        return
    except Exception as e:
        await message.answer(f"Произошла непредвиденная ошибка: {e}")
        return

    if is_private:
        await message.answer("Этот аккаунт закрыт. 🔒")
        return

    if not reels:
        await message.answer("Не найдено Reels, подходящих под условия.")
        return

    text = f"Аккаунт {username} | Подписчиков: {followers}\n\nТоп Reels:\n"
    for i, (url, views, ratio) in enumerate(reels, start=1):
        text += f"{i}. {url} | Просмотры: {views} | Популярность: {ratio:.2f}\n"

    await message.answer(text)
