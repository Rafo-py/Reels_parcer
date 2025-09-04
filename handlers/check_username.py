import os
from aiogram import Router, Bot, F
from aiogram.types import Message, FSInputFile
import database.requests as rq
import config
import re
from get_posts_count import get_instagram_post_count
from parse_posts import parse_instagram_to_csv


router = Router()
router.message.filter(F.chat.type == 'private')
API_TOKEN = config.TOKEN

bot = Bot(token=API_TOKEN)

INSTAGRAM_USERNAME_PATTERN = r'^[a-zA-Z0-9._]+$'


@router.message()
async def handle_message(message: Message):
    region = await rq.get_region(message.from_user.id)
    tg_id = message.from_user.id
    if region == 'ru':
        user_input = message.text.strip()

        if len(user_input) > 30:
            await message.answer("⚠️ Некорректный никнейм. Максимальная длина никнейма - 30 символов.")
            return

        if re.match(INSTAGRAM_USERNAME_PATTERN, user_input):
            search_message = await message.answer('Идет поиск...')
            try:
                total_posts = await get_instagram_post_count(message.text.strip())
                if total_posts:
                    await bot.edit_message_text(
                        text=f'✅ Найден пользователь @{user_input}, у него {total_posts} публикаций. Готовлю выгрузку...',
                        chat_id=message.chat.id,
                        message_id=search_message.message_id
                    )

                    await parse_instagram_to_csv(user_input, 10)

                    await bot.edit_message_text(
                        text=f'✅ Найден пользователь @{user_input}, у него {total_posts} публикаций. '
                             f'Готовлю выгрузку...\n\n'
                             f'✅ Загружены все {total_posts} медиа пользователя @{user_input}! Отправляю CSV...',
                        chat_id=message.chat.id,
                        message_id=search_message.message_id
                    )
                    file_path = f'{user_input}.csv'
                    if file_path:
                        input_file = FSInputFile(file_path)

                        with open(file_path, 'rb') as file:
                            await message.answer_document(input_file)

                        os.remove(file_path)

                    await rq.add_parsed_count(tg_id)

                    await rq.add_to_history(tg_id, user_input)
                else:
                    await bot.edit_message_text(
                        text=f"⚠️ Пользователь не найден",
                        chat_id=message.chat.id,
                        message_id=search_message.message_id
                    )
            except Exception as e:
                await bot.edit_message_text(
                    text=f"⚠️ Произошла ошибка при обработке запроса",
                    chat_id=message.chat.id,
                    message_id=search_message.message_id
                )
        else:
            await message.answer("⚠️ Некорректный никнейм. Используйте "
                                 "только буквы, цифры, точки и нижние подчеркивания.")
            return

    else:
        user_input = message.text.strip()

        if len(user_input) > 30:
            await message.answer("⚠️ Invalid username. Only letters, numbers, dots, "
                                 "and underscores are allowed (max 30 characters).")
            return

        if re.match(INSTAGRAM_USERNAME_PATTERN, user_input):
            search_message = await message.answer('Searching...')
            try:
                # Get the number of posts
                total_posts = await get_instagram_post_count(message.text.strip())
                if total_posts:
                    await bot.edit_message_text(
                        text=f'✅ Found user @{user_input}, they have {total_posts} posts. Preparing export...',
                        chat_id=message.chat.id,
                        message_id=search_message.message_id
                    )

                    await parse_instagram_to_csv(user_input, total_posts)

                    await bot.edit_message_text(
                        text=f'✅ Found user @{user_input}, they have {total_posts} posts. '
                             f'Preparing export...\n\n'
                             f'✅ All {total_posts} media from @{user_input} have been downloaded! Sending CSV...',
                        chat_id=message.chat.id,
                        message_id=search_message.message_id
                    )
                    file_path = f'{user_input}.csv'
                    if file_path:
                        input_file = FSInputFile(file_path)

                        with open(file_path, 'rb') as file:
                            await message.answer_document(input_file)

                        os.remove(file_path)

                    await rq.add_parsed_count(tg_id)

                    await rq.add_to_history(tg_id, user_input)
                else:
                    await bot.edit_message_text(
                        text=f"⚠️ User not found",
                        chat_id=message.chat.id,
                        message_id=search_message.message_id
                    )
            except Exception as e:
                await bot.edit_message_text(
                    text=f"⚠️ An error occurred while processing the request",
                    chat_id=message.chat.id,
                    message_id=search_message.message_id
                )
        else:
            await message.answer(
                "⚠️ Invalid username. Only letters, numbers, dots, and underscores are allowed (max 30 characters).")
            return
