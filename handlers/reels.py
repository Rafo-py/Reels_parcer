from aiogram import Router, types
from aiogram.filters import Command
from parse_reels import fetch_top_reels_public
import csv
import os

router = Router()

@router.message(Command("reels"))
async def get_reels(message: types.Message):
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Использование: /reels <username>")
        return

    username = args[1]
    await message.answer(f"Ищу Reels у пользователя: {username}… ⏳")

    try:
        followers, reels, is_private = fetch_top_reels_public(username, limit=10, min_ratio=0.01)
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

    # --- Создаём CSV ---
    csv_filename = f"{username}_reels.csv"
    with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["№", "URL", "Views", "Followers", "Ratio"])
        for i, (url, views, ratio) in enumerate(reels, start=1):
            writer.writerow([i, url, views, followers, f"{ratio:.2f}"])

    # Отправляем CSV пользователю
    await message.answer_document(types.FSInputFile(csv_filename))
    os.remove(csv_filename)
