"""
验证码缓存
"""
from app.caches.base import RedisStringCache
from app.caches.keys import AUTH_CODE_CACHE_KEY_PREFIX, AUTH_CODE_LIMITER_CACHE_KEY_PREFIX, USER_LOGIN_CACHE_KEY_PREFIX
from app.constants.auth_code import AUTH_CODE_EXPIRATION, TOKEN_EXPIRATION
from app.libs.datetime_kit import DateTimeKit


class AuthCodeCache(RedisStringCache):
    EXPIRATION = AUTH_CODE_EXPIRATION
    KEY_PREFIX = AUTH_CODE_CACHE_KEY_PREFIX

    def __init__(self, mobile):
        super(AuthCodeCache, self).__init__(suffix=mobile)


class AuthCodeLimiterCache(RedisStringCache):
    EXPIRATION = None
    KEY_PREFIX = AUTH_CODE_LIMITER_CACHE_KEY_PREFIX

    def __init__(self, mobile):
        super(AuthCodeLimiterCache, self).__init__(suffix=mobile)

    def get_expiration(self):
        """
        计算验证码过期时间，过期时间为每天的午夜0点
        :return:
        """
        return DateTimeKit.gen_midnight_timestamp() - DateTimeKit.get_cur_timestamp()


class UserLoginCache(RedisStringCache):
    EXPIRATION = TOKEN_EXPIRATION
    KEY_PREFIX = USER_LOGIN_CACHE_KEY_PREFIX

    def __init__(self, uid):
        super(UserLoginCache, self).__init__(suffix=uid)
