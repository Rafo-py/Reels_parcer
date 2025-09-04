from aiogram import Router, Bot, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select
import database.requests as rq
import config
from database.db import async_session
from database.requests import set_user
from database.db import User


router = Router()
router.message.filter(F.chat.type == 'private')
API_TOKEN = config.TOKEN

bot = Bot(token=API_TOKEN)


@router.message(CommandStart())
async def cmd_start(message: Message):
    await set_user(message.from_user.id, message.from_user.username or "Unknown")

    text = (f'Please select a language:')

    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🇬🇧 English', callback_data='en')],
        [InlineKeyboardButton(text='🇷🇺 Русский', callback_data='ru')]
    ])

    # Ответ пользователю
    await message.answer(text, reply_markup=markup, parse_mode=ParseMode.HTML)


@router.callback_query(F.data == 'ru')
async def main_menu_ru(callback: CallbackQuery):
    await rq.set_region(callback.from_user.id, 'ru')
    text = '''
🚀 <b>Прокачай свой Instagram-анализ!</b>

Хотите знать, какой контент заходит? Наш бот поможет проанализировать посты в секунды и получить детальную статистику в удобном <b>CSV-файле</b>!

📊 <b>Вы получите:</b> 
🔹 Просмотры 
🔹 Комментарии 
🔹 Лайки

💡 <b>Идеально для блогеров, маркетологов и аналитиков!</b>

💳 <b>Тарифы:</b>
✨ <b>Базовый:</b> 20 запросов/месяц — 1500 руб.
🚀 <b>Продвинутый:</b> 50 запросов/месяц — 2500 руб.

🎁 <b>Пробный период:</b> 2 бесплатных запроса!

⚡️ <b>Попробуйте прямо сейчас</b> — просто отправьте юзернейм Instagram!
'''
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='✨ Оформить базовый тариф', callback_data='base_tarif')],
        [InlineKeyboardButton(text='🚀 Оформить продвинутый тариф', callback_data='pro_tarif')]
    ])

    await callback.message.edit_text(text=text, reply_markup=markup, parse_mode=ParseMode.HTML)


@router.callback_query(F.data == 'en')
async def main_menu_ru(callback: CallbackQuery):
    await rq.set_region(callback.from_user.id, 'en')
    text = '''
🚀 <b>Boost Your Instagram Insights!</b>

Want to know what content goes viral? Our bot helps you analyze Instagram posts in seconds. Get detailed statistics in a structured <b>CSV file</b>!

📊 <b>You'll see: </b>
🔹 Views 
🔹 Comments 
🔹 Likes

💡 <b>Perfect for bloggers, marketers, and analysts!</b>

💳 <b>Plans:</b>
✨ <b>Basic:</b> 20 requests/month — 1500 RUB
🚀 <b>Advanced:</b> 50 requests/month — 2500 RUB

🎁 <b>Enjoy 2 free trial requests!</b>

⚡️ <b>Try it now — just send an Instagram username!</b>
'''
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='✨ Subscribe to Basic Plan', callback_data='base_tarif')],
        [InlineKeyboardButton(text='🚀 Subscribe to Advanced Plan', callback_data='pro_tarif')]
    ])

    await callback.message.edit_text(text=text, reply_markup=markup, parse_mode=ParseMode.HTML)
