
import instaloader
from typing import List, Tuple, Optional
import config

def _login(L: instaloader.Instaloader) -> None:
    """
    Login if credentials provided in config, otherwise proceed anonymously.
    """
    username = getattr(config, "INST_LOGIN", "") or ""
    password = getattr(config, "INST_PASS", "") or ""
    if username and password:
        L.login(username, password)

def fetch_top_reels(
    username: str,
    limit: int = 5,
    min_ratio: float = 0.0
) -> Tuple[int, List[Tuple[str, int, float]]]:
    """
    Returns (followers, reels) where reels is a list of tuples:
      (reel_url, views, virality_ratio)
    Sorted by virality ratio desc.
    """
    L = instaloader.Instaloader(download_pictures=False, download_videos=False, save_metadata=False, download_comments=False)
    _login(L)

    profile = instaloader.Profile.from_username(L.context, username)

    followers = profile.followers or 0
    results: List[Tuple[str, int, float]] = []

    # Iterate over posts and pick only videos (Reels are videos). Stop after reasonable count.
    count_scanned = 0
    for post in profile.get_posts():
        count_scanned += 1
        if post.is_video:
            # Prefer /reel/ link for nicer UX
            reel_url = f"https://www.instagram.com/reel/{post.shortcode}/"
            views = int(post.video_view_count or 0)
            ratio = (views / followers) if followers else 0.0
            if ratio >= min_ratio:
                results.append((reel_url, views, ratio))
        # Safety limit to avoid long scans for huge profiles
        if count_scanned >= 250:
            break

    results.sort(key=lambda x: x[2], reverse=True)
    return followers, results[:limit]
