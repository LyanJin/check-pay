from app.caches.base import RedisStringCache
from app.caches.keys import LOGIN_PASSWORD_LIMITER_CACHE_KEY_PREFIX
from app.constants.auth_code import AUTH_CODE_DAY_LIMIT_TIMES
from app.libs.datetime_kit import DateTimeKit


class UserPasswordCache(RedisStringCache):
    KEY_PREFIX = LOGIN_PASSWORD_LIMITER_CACHE_KEY_PREFIX

    def __init__(self, mobile_name):
        super(UserPasswordCache, self).__init__(suffix=mobile_name)

    def get_expiration(self):
        """
        计算密码错误次数过期时间，过期时间为每天的午夜0点
        :return:
        """
        return DateTimeKit.gen_midnight_timestamp() - DateTimeKit.get_cur_timestamp()


class UserPasswordLimitCache:

    def __init__(self, mobile_number):
        self.mobile_number = mobile_number
        self.cache = UserPasswordCache(self.mobile_number)

    def incr_times(self):
        """
        发送次数+1
        :return:
        """
        times = self.cache.incr()
        self.cache.update_expiration()
        return times

    def is_limited(self):
        """
        是否已经达到当天限制
        :return:
        """
        return self.get_times() >= AUTH_CODE_DAY_LIMIT_TIMES

    def delete_cache(self):
        """
        删除该缓存
        :return:
        """
        return self.cache.delete_cache()

    def get_times(self):
        """
        获取已经错误的次数
        :return:
        """
        return int(self.cache.loads() or 0)
