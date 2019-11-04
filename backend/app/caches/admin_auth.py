from app.caches.base import RedisStringCache
from app.caches.keys import ADMIN_LOGIN_CACHE_KEY_PREFIX
from app.constants.auth_code import TOKEN_EXPIRATION_ADMIN


class AdminLoginCache(RedisStringCache):
    EXPIRATION = TOKEN_EXPIRATION_ADMIN
    KEY_PREFIX = ADMIN_LOGIN_CACHE_KEY_PREFIX

    def __init__(self, uid):
        super(AdminLoginCache, self).__init__(suffix=uid)
