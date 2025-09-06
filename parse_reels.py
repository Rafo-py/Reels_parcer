import requests
from bs4 import BeautifulSoup
from typing import List, Tuple
import json
import time

def fetch_top_reels_public(username: str, limit: int = 5, min_ratio: float = 0.0) -> Tuple[int, List[Tuple[str, int, float]], bool]:
    """
    Парсит публичный Instagram аккаунт и возвращает:
        followers: int - количество подписчиков
        reels: List[Tuple[reel_url:str, views:int, ratio:float]]
        is_private: bool - True если аккаунт закрыт
    Работает только с публичными аккаунтами.
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
    except requests.RequestException:
        raise ValueError("Ошибка подключения к Instagram")

    if response.status_code != 200:
        raise ValueError("Аккаунт не найден или ошибка доступа")

    # Проверка закрытого аккаунта
    if "This Account is Private" in response.text:
        return 0, [], True

    followers = 0
    results: List[Tuple[str, int, float]] = []

    # Парсим JSON из скрипта
    soup = BeautifulSoup(response.text, "html.parser")
    script_tag = None
    for script in soup.find_all("script", type="text/javascript"):
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
        for edge in edges:
            if edge["node"]["__typename"] == "GraphVideo":
                shortcode = edge["node"]["shortcode"]
                views = edge["node"]["video_view_count"]
                ratio = (views / followers) if followers else 0.0

                if ratio >= min_ratio:
                    reel_url = f"https://www.instagram.com/reel/{shortcode}/"
                    results.append((reel_url, views, ratio))

            if len(results) >= limit:
                break

    except Exception:
        return followers, results[:limit], False

    # Сортировка по популярности (ratio)
    results.sort(key=lambda x: x[2], reverse=True)
    return followers, results[:limit], False

# --- Пример использования ---
if __name__ == "__main__":
    username = "instagram"
    followers, reels, is_private = fetch_top_reels_public(username, limit=5, min_ratio=0.01)
    print(f"Followers: {followers}, Private: {is_private}")
    for url, views, ratio in reels:
        print(f"{url} | Views: {views} | Ratio: {ratio:.2f}")
