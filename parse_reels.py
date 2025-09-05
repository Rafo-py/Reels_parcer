import instaloader
from typing import List, Tuple

def fetch_top_reels_public(username: str, limit: int = 5, min_ratio: float = 0.0) -> Tuple[int, List[Tuple[str, int, float]], bool]:
    """
    Возвращает:
      followers, reels (url, views, ratio), is_private
    Работает только с публичными аккаунтами, без логина.
    """
    L = instaloader.Instaloader(
        download_pictures=False,
        download_videos=False,
        save_metadata=False,
        download_comments=False,
        post_metadata_txt_pattern="",  # не сохраняем локально
    )
    try:
        profile = instaloader.Profile.from_username(L.context, username)
    except instaloader.exceptions.ProfileNotExistsException:
        raise ValueError("Аккаунт не найден")
    
    if profile.is_private:
        return 0, [], True  # аккаунт закрыт

    followers = profile.followers or 0
    results: List[Tuple[str, int, float]] = []

    count_scanned = 0
    for post in profile.get_posts():
        count_scanned += 1
        if post.is_video:
            reel_url = f"https://www.instagram.com/reel/{post.shortcode}/"
            views = int(post.video_view_count or 0)
            ratio = (views / followers) if followers else 0.0
            if ratio >= min_ratio:
                results.append((reel_url, views, ratio))
        if count_scanned >= 250:
            break

    results.sort(key=lambda x: x[2], reverse=True)
    return followers, results[:limit], False
