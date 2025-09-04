from aiogram import F, Router, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.types import (InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.types import ContentType
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
import asyncio
import time

import config

import database.requests as rq

router = Router()
router.message.filter(F.chat.type == 'private')
API_TOKEN = config.TOKEN

bot = Bot(token=API_TOKEN)


class BroadcastStates(StatesGroup):
    message_text = State()
    media_files = State()
    button_text = State()
    button_url = State()
    confirmation = State()


@router.message(F.text == "/sender")
async def start_broadcast(message: Message, state: FSMContext):
    if message.from_user.id != config.ADMIN_ID:
        return

    await message.answer("Введите текст для рассылки (поддерживается MarkdownV2):")
    await state.set_state(BroadcastStates.message_text)


@router.message(BroadcastStates.message_text)
async def input_message_text(message: Message, state: FSMContext):
    await state.update_data(message_text=message.md_text)
    await message.answer("Прикрепите фото или напишите 'нет', если не надо:")
    await state.set_state(BroadcastStates.media_files)


@router.message(BroadcastStates.media_files, F.content_type.in_([ContentType.PHOTO, ContentType.TEXT]))
async def input_media_files(message: Message, state: FSMContext):
    if message.text and message.text.lower() == "нет":
        await state.update_data(media_files=[])
    elif message.photo:
        await state.update_data(media_files=[message.photo[-1].file_id])

    await message.answer("Введите текст кнопки (или напишите 'нет', если кнопка не нужна):")
    await state.set_state(BroadcastStates.button_text)


@router.message(BroadcastStates.button_text)
async def input_button_text(message: Message, state: FSMContext):
    if message.text.lower() == "нет":
        await state.update_data(button_text=None, button_url=None)
        await ask_confirmation(message, state)
    else:
        await state.update_data(button_text=message.text)
        await message.answer("Введите URL кнопки:")
        await state.set_state(BroadcastStates.button_url)


@router.message(BroadcastStates.button_url)
async def input_button_url(message: Message, state: FSMContext):
    await state.update_data(button_url=message.text)
    await ask_confirmation(message, state)


async def ask_confirmation(message: Message, state: FSMContext):
    data = await state.get_data()

    message_text = data["message_text"]
    media_files = data.get("media_files")
    button_text = data.get("button_text")
    button_url = data.get("button_url")

    keyboard = None
    if button_text and button_url:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=button_text, url=button_url)]
        ])

    if media_files:
        await message.answer_photo(
            photo=media_files[0],
            caption=message_text,
            reply_markup=keyboard,
            parse_mode="MarkdownV2"
        )
    else:
        await message.answer(
            text=message_text,
            reply_markup=keyboard,
            parse_mode="MarkdownV2"
        )

    confirmation_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Начать рассылку", callback_data="confirm_send")],
            [InlineKeyboardButton(text="Отменить", callback_data="cancel_send")]
        ]
    )
    await message.answer("Отправить рассылку?", reply_markup=confirmation_keyboard)
    await state.set_state(BroadcastStates.confirmation)


@router.callback_query(BroadcastStates.confirmation)
async def confirm_or_cancel(callback: CallbackQuery, state: FSMContext):
    if callback.data == "confirm_send":
        data = await state.get_data()
        subscription_type = 'All'

        users = await rq.get_filtered_users_sender(subscription_type=subscription_type)
        total_users = len(users)
        sent_count = 0

        start_time = time.time()

        for user in users:
            try:
                await send_broadcast(user["tg_id"], data)
                sent_count += 1
                await asyncio.sleep(0.05)
            except Exception as e:
                print(f"Ошибка отправки для {user['tg_id']}: {e}")

        end_time = time.time()
        duration = round(end_time - start_time, 2)

        await callback.message.answer(
            f"Рассылка завершена. Отправлено {sent_count}/{total_users} сообщений за {duration} секунд."
        )
    else:
        await callback.message.answer("Рассылка отменена.")

    await state.clear()
    await callback.answer()


async def send_broadcast(user_id, data):
    text = data["message_text"]
    media_files = data.get("media_files")
    button_text = data.get("button_text")
    button_url = data.get("button_url")

    keyboard = None
    if button_text and button_url:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=button_text, url=button_url)]
        ])

    if media_files:
        await bot.send_photo(user_id, photo=media_files[0], caption=text, reply_markup=keyboard,
                             parse_mode="MarkdownV2")
    else:
        await bot.send_message(user_id, text, reply_markup=keyboard, parse_mode="MarkdownV2")
