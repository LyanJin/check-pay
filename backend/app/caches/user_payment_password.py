from app.caches.base import RedisStringCache
from app.caches.keys import LOGIN_PAYMENT_PASSWORD_LIMITER_CACHE_KEY_PREFIX
from app.constants.trade import PAYMENT_PASSWORD_ERROR_LIMIT_TIMES
from app.libs.datetime_kit import DateTimeKit


class UserPaymentPasswordCache(RedisStringCache):
    KEY_PREFIX = LOGIN_PAYMENT_PASSWORD_LIMITER_CACHE_KEY_PREFIX

    def __init__(self, uid):
        super(UserPaymentPasswordCache, self).__init__(suffix=uid)

    def get_expiration(self):
        """
        计算交易密码错误次数过期时间，过期时间为每天的午夜0点
        :return:
        """
        return DateTimeKit.gen_midnight_timestamp() - DateTimeKit.get_cur_timestamp()


class UserPaymentPasswordLimitCache:

    def __init__(self, uid):
        self.uid = uid
        self.cache = UserPaymentPasswordCache(self.uid)

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
        return self.get_left_times() == 0

    def get_left_times(self):
        """
        剩余可用次数
        :return:
        """
        times = int(self.cache.loads() or 0)
        return max(PAYMENT_PASSWORD_ERROR_LIMIT_TIMES - times, 0)

    def delete_cache(self):
        """
        删除该缓存
        :return:
        """
        return self.cache.delete_cache()
