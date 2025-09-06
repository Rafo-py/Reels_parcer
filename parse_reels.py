import requests
from bs4 import BeautifulSoup
from typing import List, Tuple
import json

def fetch_top_reels_public(username: str, limit: int = 10, min_ratio: float = 0.01) -> Tuple[int, List[Tuple[str, int, float]], bool]:
    """
    Получает топ Reels публичного аккаунта.
    Возвращает:
        followers: int
        reels: List[Tuple[url:str, views:int, ratio:float]]
        is_private: bool
    """
    profile_url = f"https://www.instagram.com/{username}/"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/117.0.0.0 Safari/537.36"
        )
    }

    try:
        response = requests.get(profile_url, headers=headers, timeout=10)
        if response.status_code != 200:
            raise ValueError("Аккаунт не найден или ошибка доступа")
    except requests.RequestException:
        raise ValueError("Ошибка подключения к Instagram")

    if "This Account is Private" in response.text:
        return 0, [], True

    # Получаем JSON из скрипта window._sharedData
    soup = BeautifulSoup(response.text, "html.parser")
    script_tag = None
    for script in soup.find_all("script"):
        if script.string and "window._sharedData" in script.string:
            script_tag = script.string
            break

    if not script_tag:
        return 0, [], False

    try:
        json_str = script_tag.strip().replace("window._sharedData = ", "")[:-1]
        data = json.loads(json_str)
        user_data = data["entry_data"]["ProfilePage"][0]["graphql"]["user"]

        followers = user_data["edge_followed_by"]["count"]
        edges = user_data["edge_owner_to_timeline_media"]["edges"]

        reels = []
        for edge in edges:
            node = edge["node"]
            if node["__typename"] == "GraphVideo":
                shortcode = node["shortcode"]
                views = node.get("video_view_count", 0)
                ratio = (views / followers) if followers else 0
                if ratio >= min_ratio:
                    reels.append((f"https://www.instagram.com/reel/{shortcode}/", views, ratio))
        # сортировка по популярности
        reels.sort(key=lambda x: x[2], reverse=True)
        return followers, reels[:limit], False

    except Exception:
        return 0, [], False
