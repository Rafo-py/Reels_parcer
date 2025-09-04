import sqlite3
import csv
import os
from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile
from io import StringIO

import config

API_TOKEN = config.TOKEN
bot = Bot(token=API_TOKEN)
router = Router()


def convert_db_to_csv(db_path: str, output_csv_path: str):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    with open(output_csv_path, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)

        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()

            writer.writerow([f"Table: {table_name}"])

            column_names = [description[0] for description in cursor.description]
            writer.writerow(column_names)

            writer.writerows(rows)

            writer.writerow([])

    conn.close()


@router.message(Command('base'))
async def send_base_file(message: Message):
    if message.from_user.id != config.ADMIN_ID:
        return
    db_path = 'db.sqlite3'
    csv_path = 'database_export.csv'

    try:
        convert_db_to_csv(db_path, csv_path)

        input_file = FSInputFile(csv_path)
        await message.answer_document(input_file)

        os.remove(csv_path)

    except Exception as e:
        await message.answer(f"⚠️ Произошла ошибка при создании файла: {str(e)}")

