import instaloader

import config


async def get_instagram_post_count(username):
    instaloader_username = config.INST_LOGIN
    instaloader_password = config.INST_PASS

    L = instaloader.Instaloader()

    L.context.user_agent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/537.36'

    L.login(instaloader_username, instaloader_password)

    profile = instaloader.Profile.from_username(L.context, username)

    post_count = profile.mediacount

    return post_count
