import instaloader

async def get_instagram_reels_count(username: str) -> int:
    """
    Возвращает количество Reels (видео) у пользователя.
    Работает без логина, только публичные аккаунты.
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
        count = 0
        for post in profile.get_posts():
            if post.is_video:  # Только Reels
                count += 1
        return count
    except Exception:
        return 0
