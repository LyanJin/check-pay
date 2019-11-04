from app.caches.base import RedisStringCache
from app.caches.keys import MERCHANT_LOGIN_CACHE_KEY_PREFIX
from app.constants.auth_code import TOKEN_EXPIRATION_MERCHANT


class MerchantLoginCache(RedisStringCache):
    EXPIRATION = TOKEN_EXPIRATION_MERCHANT
    KEY_PREFIX = MERCHANT_LOGIN_CACHE_KEY_PREFIX

    def __init__(self, uid):
        super(MerchantLoginCache, self).__init__(suffix=uid)
