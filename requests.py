import datetime

from database.db import async_session, History
from database.db import User
from sqlalchemy import select
from aiogram import Bot
from config import TOKEN

bot = Bot(token=TOKEN)


async def set_user(tg_id: int, username: str):
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(
                select(User).where(User.tg_id == tg_id)
            )
            user = result.scalar_one_or_none()

            if user:
                user.tg_username = username
            else:
                user = User(
                    tg_id=tg_id,
                    tg_username=username,
                )
                session.add(user)

            await session.commit()


async def set_region(tg_id: int, region: str):
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(
                select(User).where(User.tg_id == tg_id)
            )
            user = result.scalar_one_or_none()

            user.region = region
            session.add(user)

            await session.commit()


async def get_region(tg_id: int) -> str | None:
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(
                select(User.region).where(User.tg_id == tg_id)
            )
            user_region = result.scalar_one_or_none()

            return user_region


async def get_filtered_users_sender(subscription_type: str):
    async with async_session() as session:
        async with session.begin():
            query = select(User)

            result = await session.execute(query)
            users = result.scalars().all()

            return [
                {
                    'tg_id': user.tg_id

                }
                for user in users
            ]


async def get_all_users():
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(select(User))
            users = result.scalars().all()

            users_list = [
                {
                    'tg_id': user.tg_id,
                    'tg_username': user.tg_username,
                    'user_name': user.user_name,
                    'phone_number': user.phone_number if user.phone_number else 'не указан'
                }
                for user in users
            ]
            return users_list


async def get_utc_plus_3_time():
    utc_plus_3 = datetime.timezone(datetime.timedelta(hours=3))

    current_time_utc_plus_3 = datetime.datetime.now(utc_plus_3)

    return current_time_utc_plus_3.strftime('%d.%m.%Y %H:%M')


async def add_to_history(tg_id, parsed):
    async with async_session() as session:
        async with session.begin():
            add = History(
                tg_id=tg_id,
                date=await get_utc_plus_3_time(),
                username_parsed=parsed
            )
            session.add(add)

            await session.commit()


async def add_parsed_count(tg_id):
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(
                select(User).where(User.tg_id == tg_id)
            )
            user = result.scalar_one_or_none()

            user.rq_count += 1
            session.add(user)

            await session.commit()