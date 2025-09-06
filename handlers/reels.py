from aiogram import Router, types
from aiogram.filters import Command
import csv
import os
from parse_reels import fetch_top_reels_public  # Новый рабочий метод с instagram-scraper

router = Router()

@router.message(Command("reels"))
async def get_reels(message: types.Message):
    """
    Обработчик команды /reels <username>
    Парсит публичный Instagram аккаунт и возвращает топ Reels в CSV.
    """
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Использование: /reels <username>")
        return

    username = args[1]
    search_msg = await message.answer(f"Ищу Reels у пользователя: {username}… ⏳")

    try:
        followers, reels, is_private = fetch_top_reels_public(username, limit=10)
    except ValueError as e:
        await search_msg.edit_text(f"Ошибка: {e}")
        return
    except Exception as e:
        await search_msg.edit_text(f"Произошла непредвиденная ошибка: {e}")
        return

    if is_private:
        await search_msg.edit_text("Этот аккаунт закрыт. 🔒")
        return

    if not reels:
        await search_msg.edit_text("Не найдено Reels.")
        return

    # Создаём CSV
    csv_filename = f"{username}_reels.csv"
    with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["№", "URL", "Views", "Followers", "Ratio"])
        for i, (url, views, ratio) in enumerate(reels, start=1):
            writer.writerow([i, url, views, followers, f"{ratio:.2f}"])

    # Отправка CSV
    await search_msg.edit_text(f"Готово! Отправляю CSV с топ {len(reels)} Reels.")
    await message.answer_document(types.FSInputFile(csv_filename))

    # Удаляем временный файл
    os.remove(csv_filename)
