import subprocess
import json
import os
from typing import List, Tuple

def fetch_top_reels_public(username: str, limit: int = 5) -> Tuple[int, List[Tuple[str, int, float]], bool]:
    """
    Парсинг публичных Reels через instagram-scraper (без логина)
    Возвращает followers, список топ Reels и приватность аккаунта
    """
    try:
        # Создаём папку для временных данных
        os.makedirs(f"./temp_data/{username}", exist_ok=True)

        # Запускаем instagram-scraper для видео
        subprocess.run([
            "instagram-scraper", username,
            "--media-types", "video",
            "--maximum", str(limit),
            "--destination", f"./temp_data/{username}",
            "--quiet"
        ], check=True)

        # Читаем posts.json
        reels_data = []
        followers = 0
        posts_file = f"./temp_data/{username}/{username}.json"

        if not os.path.exists(posts_file):
            return 0, [], False

        with open(posts_file, "r", encoding="utf-8") as f:
            for line in f:
                post = json.loads(line)
                if followers == 0:
                    followers = post.get("owner", {}).get("edge_followed_by", 0)
                if post.get("media_type") == "video":
                    url = post.get("shortcode")
                    views = post.get("video_view_count", 0)
                    ratio = (views / followers) if followers else 0.0
                    reels_data.append((f"https://www.instagram.com/reel/{url}/", views, ratio))

        # Сортируем по популярности
        reels_data.sort(key=lambda x: x[2], reverse=True)

        return followers, reels_data[:limit], False

    except Exception:
        return 0, [], False
