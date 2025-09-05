import instaloader
from typing import List, Tuple

def fetch_top_reels_public(
    username: str,
    limit: int = 5,
    min_ratio: float = 0.0
) -> Tuple[int, List[Tuple[str, int, float]], bool]:
    """
    Возвращает (followers, reels, is_private)
    reels — список кортежей: (reel_url, views, virality_ratio)
    is_private — True если аккаунт закрыт
    """
    L = instaloader.Instaloader(
        download_pictures=False,
        download_videos=False,
        save_metadata=False,
        download_comments=False
    )

    try:
        profile = instaloader.Profile.from_username(L.context, username)
    except instaloader.exceptions.ProfileNotExistsException:
        return 0, [], False  # аккаунт не найден
    except instaloader.exceptions.PrivateProfileNotFollowedException:
        return 0, [], True  # закрытый аккаунт

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
    return followers, results[:limit], profile.is_private
