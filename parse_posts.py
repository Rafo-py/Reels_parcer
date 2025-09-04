import instaloader
import csv
import asyncio
from concurrent.futures import ThreadPoolExecutor
from itertools import islice
import time
import config
import codecs

def parse_post(post, followers, post_data_list):
    post_url = f"https://www.instagram.com/p/{post.shortcode}/"

    views = post.video_view_count if post.is_video else None
    virus_factor = views / followers if views else 0

    post_type = 'Рилс' if post.is_video else 'Пост'

    post_data = [
        post_url,
        views if views else 'Нет просмотров',
        post.likes,
        post.comments,
        f"{virus_factor:.2f}",
        post_type,
        post.date_utc,
        post.caption
    ]
    print(post_data)
    post_data_list.append(post_data)


async def parse_instagram_to_csv(target_username, num_posts=20):
    L = instaloader.Instaloader()

    L.context.user_agent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/537.36'

    try:
        L.login(config.INST_LOGIN, config.INST_PASS)
    except instaloader.exceptions.InstaloaderException as e:
        print(f"Ошибка при логине: {e}")
        return None

    profile = instaloader.Profile.from_username(L.context, target_username)
    followers = profile.followers

    csv_filename = f"{target_username}.csv"
    csv_header = ['Ссылка', 'Просмотры', 'Лайки', 'Комментарии', 'Вирусность', 'Тип', 'Дата публикации', 'Описание']

    post_data_list = []

    loop = asyncio.get_event_loop()

    with ThreadPoolExecutor(max_workers=2) as executor:
        tasks = []
        for post in islice(profile.get_posts(), num_posts):
            tasks.append(loop.run_in_executor(executor, parse_post, post, followers, post_data_list))

            await asyncio.sleep(3)

        try:
            await asyncio.gather(*tasks)
        except instaloader.exceptions.InstaloaderException as e:
            if "Too many queries" in str(e):
                print("Слишком много запросов. Ожидаем блокировку...")
                with open(csv_filename, mode='w', newline='', encoding='utf-8-sig') as file:
                    writer = csv.writer(file)
                    writer.writerow(csv_header)
                    writer.writerows(post_data_list)
                print(f"Данные сохранены в {csv_filename} из-за блокировки.")
                return csv_filename
            else:
                print(f"Ошибка при обработке: {e}")
                return None

    post_data_list.sort(key=lambda x: float(x[4]), reverse=True)

    with open(csv_filename, mode='w', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file)
        writer.writerow(csv_header)
        writer.writerows(post_data_list)

    return csv_filename
