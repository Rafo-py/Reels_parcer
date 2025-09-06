# handlers/reels.py
import os
import csv
from aiogram import Router, types
from aiogram.filters import Command
from parse_reels import parse_instagram_reels_to_csv
from get_reels_count import get_instagram_reels_count
router = Router()


@router.message(Command("reels"))
async def get_reels(message: types.Message):
    """
    Обработчик команды /reels <username>
    Парсит публичный Instagram аккаунт и отправляет Reels в CSV.
    """
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Использование: /reels <username>")
        return

    username = args[1].strip().lstrip("@")
    await message.answer(f"🔎 Ищу Reels у пользователя @{username}…")

    try:
        # Получаем количество Reels
        total_reels = get_instagram_reels_count(username)
        if total_reels == 0:
            await message.answer("❌ Reels не найдены или аккаунт закрыт.")
            return

        # Парсим Reels в CSV (ограничим, например, 20 штук)
        csv_filename = f"{username}_reels.csv"
        parse_instagram_reels_to_csv(username, limit=20, output_file=csv_filename)

        # Отправляем CSV пользователю
        await message.answer_document(types.FSInputFile(csv_filename))

        # Удаляем временный файл
        os.remove(csv_filename)

    except Exception as e:
        await message.answer(f"⚠️ Ошибка при обработке: {e}")
