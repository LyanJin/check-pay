import functools

from flask import request

from app.extensions import redis
from app.libs.error_code import RequestRateLimit
from app.libs.ip_kit import IpKit


class Limiter:

    @classmethod
    def parse_period(cls, period):
        if period == 'second':
            return 1
        if period == 'minute':
            return 1 * 60
        if period == 'hour':
            return 1 * 60 * 60
        if period == 'day':
            return 1 * 60 * 60 * 24
        return int(period)

    @classmethod
    def parse_condition(cls, cond):
        if isinstance(cond, str):
            times, period = cond.split('/')
        else:
            times, period = cond

        times = int(times)
        return times, cls.parse_period(period)

    @classmethod
    def get_limit_key(cls):
        path = request.path
        ip = IpKit.get_remote_ip()
        return f"{path}:{ip}"

    @classmethod
    def is_limited(cls, condition, key):
        limit, period = cls.parse_condition(condition)
        value = redis.incr(key)
        over_cond = value > limit
        if not over_cond:
            redis.expire(key, period)
        # ttl = redis.ttl(key)
        # print(f"key: {key}, limit: {limit}, value: {value}, ttl: {ttl}, over_cond: {over_cond}")
        return over_cond

    @classmethod
    def limit(cls, condition):
        """
        限制访问速度
        :param condition:
            1/second: 一秒钟内一次
            1/minute：一分钟内一次
            1/hour：一小时内一次
            1/day：一天内：一次
            1/1：一秒钟内一次
            2/60：60秒钟内2次
            (2, 60)：60秒钟内2次
        :return:
        """
        def _limit(func):
            @functools.wraps(func)
            def __limit(*args, **kwargs):
                key = cls.get_limit_key()
                if cls.is_limited(condition, key):
                    return RequestRateLimit().as_response()
                return func(*args, **kwargs)

            return __limit

        return _limit


if __name__ == '__main__':
    print(Limiter.parse_condition("1/second"))
    print(Limiter.parse_condition("1/minute"))
    print(Limiter.parse_condition("1/hour"))
    print(Limiter.parse_condition("1/day"))
    print(Limiter.parse_condition("1/1"))
    print(Limiter.parse_condition("2/60"))
    print(Limiter.parse_condition((2, 60)))
