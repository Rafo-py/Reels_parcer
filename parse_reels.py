import instaloader
import csv
import os

def parse_instagram_reels_to_csv(username: str, max_count: int = 50):
    """
    Скачивает информацию о Reels пользователя и сохраняет в CSV.
    Работает без логина, только для публичных аккаунтов.
    """
    L = instaloader.Instaloader(
        download_pictures=False,
        download_videos=False,
        download_video_thumbnails=False,
        save_metadata=False,
        compress_json=False,
    )

    try:
        profile = instaloader.Profile.from_username(L.context, username)
    except Exception as e:
        raise ValueError(f"Ошибка доступа к аккаунту: {e}")

    # Создаем CSV
    filename = f"{username}_reels.csv"
    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["№", "Shortcode", "URL", "Views", "Likes", "Comments"])

        count = 0
        for post in profile.get_posts():
            if not post.is_video:  # Берем только Reels
                continue

            count += 1
            shortcode = post.shortcode
            url = f"https://www.instagram.com/reel/{shortcode}/"
            views = post.video_view_count or 0
            likes = post.likes or 0
            comments = post.comments or 0

            writer.writerow([count, shortcode, url, views, likes, comments])

            if count >= max_count:
                break

    return filename
