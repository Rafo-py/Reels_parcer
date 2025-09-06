import requests
from typing import List, Tuple
import json

def fetch_top_reels_public(username: str, limit: int = 5, min_ratio: float = 0.0) -> Tuple[int, List[Tuple[str, int, float]], bool]:
    """
    Парсит публичный Instagram аккаунт через JSON и возвращает:
        followers: int - количество подписчиков
        reels: List[Tuple[reel_url:str, views:int, ratio:float]]
        is_private: bool - True если аккаунт закрыт
    Работает только с публичными аккаунтами.
    """
    profile_url = f"https://www.instagram.com/{username}/?__a=1&__d=dis"

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

    data = response.json()

    user_data = data.get("graphql", {}).get("user")
    if not user_data:
        return 0, [], False

    if user_data.get("is_private"):
        return 0, [], True

    followers = user_data.get("edge_followed_by", {}).get("count", 0)

    edges = user_data.get("edge_owner_to_timeline_media", {}).get("edges", [])
    results: List[Tuple[str, int, float]] = []

    for edge in edges:
        node = edge.get("node", {})
        if node.get("__typename") == "GraphVideo":
            shortcode = node.get("shortcode")
            views = node.get("video_view_count", 0)
            ratio = (views / followers) if followers else 0.0
            if ratio >= min_ratio:
                reel_url = f"https://www.instagram.com/reel/{shortcode}/"
                results.append((reel_url, views, ratio))

        if len(results) >= limit:
            break

    # Сортировка по популярности
    results.sort(key=lambda x: x[2], reverse=True)

    return followers, results[:limit], False

# --- Пример использования ---
if __name__ == "__main__":
    username = "instagram"
    followers, reels, is_private = fetch_top_reels_public(username, limit=5, min_ratio=0.01)
    print(f"Followers: {followers}, Private: {is_private}")
    for url, views, ratio in reels:
        print(f"{url} | Views: {views} | Popularity: {ratio:.2f}")
