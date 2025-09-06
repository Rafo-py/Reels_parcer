import requests
from typing import List, Tuple
import json
import csv

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

    if "This Account is Private" in response.text:
        return 0, [], True

    # Парсим JSON из window._sharedData
    script_tag = None
    for line in response.text.splitlines():
        if "window._sharedData" in line:
            script_tag = line
            break

    if not script_tag:
        return 0, [], False

    try:
        json_str = script_tag.strip().replace("window._sharedData = ", "")[:-1]
        data = json.loads(json_str)
        user_data = data["entry_data"]["ProfilePage"][0]["graphql"]["user"]

        followers = user_data["edge_followed_by"]["count"]

        edges = user_data["edge_owner_to_timeline_media"]["edges"]
        reels: List[Tuple[str, int, float]] = []

        for edge in edges:
            node = edge["node"]
            if node["__typename"] == "GraphVideo":
                shortcode = node["shortcode"]
                views = node.get("video_view_count", 0)
                ratio = views / followers if followers else 0.0

                if ratio >= min_ratio:
                    reel_url = f"https://www.instagram.com/reel/{shortcode}/"
                    reels.append((reel_url, views, ratio))

        # Сортируем по популярности
        reels.sort(key=lambda x: x[2], reverse=True)

        return followers, reels[:limit], False

    except Exception:
        return 0, [], False


def export_reels_to_csv(username: str, reels: List[Tuple[str, int, float]]):
    """Создаёт CSV с результатами"""
    filename = f"{username}_reels.csv"
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["№", "URL", "Views", "Popularity Ratio"])
        for i, (url, views, ratio) in enumerate(reels, start=1):
            writer.writerow([i, url, views, f"{ratio:.4f}"])
    return filename


# --- Пример использования ---
if __name__ == "__main__":
    username = "instagram"
    followers, reels, is_private = fetch_top_reels_public(username, limit=10, min_ratio=0.0)

    if is_private:
        print(f"Аккаунт {username} закрыт.")
    else:
        print(f"Подписчиков: {followers}")
        for i, (url, views, ratio) in enumerate(reels, start=1):
            print(f"{i}. {url} | Views: {views} | Ratio: {ratio:.4f}")

        csv_file = export_reels_to_csv(username, reels)
        print(f"CSV сохранён: {csv_file}")
