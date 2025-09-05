import os
import re
import logging
from aiogram import Router, F
from aiogram.types import Message, FSInputFile
import database.requests as rq
import config
from get_posts_count import get_instagram_post_count
from parse_posts import parse_instagram_to_csv

# Настройка логирования
logging.basicConfig(level=logging.INFO)

router = Router()
router.message.filter(F.chat.type == 'private')

INSTAGRAM_USERNAME_PATTERN = r'^[a-zA-Z0-9._]{1,30}$'  # Ограничение длины сразу

@router.message()
async def handle_message(message: Message):
    try:
        region = await rq.get_region(message.from_user.id)
        tg_id = message.from_user.id
        user_input = message.text.strip()

        # Проверка никнейма
        if not re.match(INSTAGRAM_USERNAME_PATTERN, user_input):
            warning_text = "⚠️ Некорректный никнейм. Используйте только буквы, цифры, точки и нижние подчеркивания (max 30 символов)." \
                if region == 'ru' else \
                "⚠️ Invalid username. Only letters, numbers, dots, and underscores are allowed (max 30 characters)."
            await message.answer(warning_text)
            return

        # Отправляем начальное сообщение о поиске
        search_message = await message.answer('Идет поиск...' if region == 'ru' else 'Searching...')

        try:
            # Получаем количество постов пользователя
            total_posts = await get_instagram_post_count(user_input)
            if not total_posts:
                warning_text = f"⚠️ Пользователь не найден" if region == 'ru' else "⚠️ User not found"
                await safe_edit_message(message, search_message, warning_text)
                return

            # Редактируем сообщение о найденном пользователе
            info_text = f"✅ Найден пользователь @{user_input}, у него {total_posts} публикаций. Готовлю выгрузку..." \
                if region == 'ru' else \
                f"✅ Found user @{user_input}, they have {total_posts} posts. Preparing export..."
            await safe_edit_message(message, search_message, info_text)

            # Парсим посты в CSV
            await parse_instagram_to_csv(user_input, total_posts if region != 'ru' else 10)

            # Финальное сообщение
            final_text = f"✅ Загружены все {total_posts} медиа пользователя @{user_input}! Отправляю CSV..." \
                if region == 'ru' else \
                f"✅ All {total_posts} media from @{user_input} have been downloaded! Sending CSV..."
            await safe_edit_message(message, search_message, final_text)

            # Отправка CSV
            file_path = f'{user_input}.csv'
            if os.path.exists(file_path):
                input_file = FSInputFile(file_path)
                await message.answer_document(input_file)
                os.remove(file_path)

            # Обновление статистики
            await rq.add_parsed_count(tg_id)
            await rq.add_to_history(tg_id, user_input)

        except Exception as e:
            logging.error(f"Ошибка при обработке запроса: {e}")
            await safe_edit_message(message, search_message,
                                    "⚠️ Произошла ошибка при обработке запроса" if region == 'ru'
                                    else "⚠️ An error occurred while processing the request")

    except Exception as e_outer:
        logging.error(f"Ошибка во внешнем блоке: {e_outer}")
        await message.answer("⚠️ Произошла ошибка при обработке вашего сообщения")

# Вспомогательная функция для безопасного редактирования сообщения
async def safe_edit_message(message: Message, search_message: Message, text: str):
    try:
        if search_message:
            await message.bot.edit_message_text(
                text=text,
                chat_id=message.chat.id,
                message_id=search_message.message_id
            )
        else:
            await message.answer(text)
    except Exception as e:
        logging.warning(f"Не удалось отредактировать сообщение: {e}")
        await message.answer(text)
