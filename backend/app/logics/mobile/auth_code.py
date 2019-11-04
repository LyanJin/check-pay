from flask import current_app

from app.caches.auth_code import AuthCodeCache, AuthCodeLimiterCache
from app.constants.auth_code import AUTH_CODE_DAY_LIMIT_TIMES, AUTH_CODE_LENGTH, SPECIAL_SMS_AUTH_CODE
from app.libs.string_kit import RandomString
from app.libs.error_code import AuthCodeExpiredError


class AuthCodeGenerator:

    def __init__(self, mobile_number):
        self.mobile_number = mobile_number
        self.cache = AuthCodeCache(self.mobile_number)

    def generate_code(self):
        """
        生成验证码并缓存
        :return:
        """

        code = RandomString.gen_random_str(AUTH_CODE_LENGTH)

        r = self.cache.dumps(code)

        # current_app.logger.info('dumps code to redis, r: %s', r)

        return code

    def is_expired(self, code):
        """
        检查验证码是否已经过期
        :param code:
        :return:
        """
        if (current_app.config['DEBUG'] or current_app.config['TESTING']) and code == SPECIAL_SMS_AUTH_CODE:
            return False

        cache_code = self.cache.loads()

        # 只要没有取到验证码就认为是过期的
        return not cache_code

    def verify_code(self, code):
        """
        验证验证码是否匹配
        :param code:
        :return:
        """
        if (current_app.config['DEBUG'] or current_app.config['TESTING']) and code == SPECIAL_SMS_AUTH_CODE:
            return True

        cache_code = self.cache.loads()

        # current_app.logger.info('code: %s, cache_code: %s', code, cache_code)

        return code == cache_code


class AuthCodeLimiter:

    def __init__(self, mobile_number):
        self.mobile_number = mobile_number
        self.cache = AuthCodeLimiterCache(self.mobile_number)

    def get_times(self):
        """
        获得已经发送的次数
        :return:
        """
        return int(self.cache.loads() or 0)

    def is_limited(self):
        """
        是否已经达到当天限制
        :return:
        """
        return self.get_times() >= AUTH_CODE_DAY_LIMIT_TIMES

    def incr_times(self):
        """
        发送次数+1
        :return:
        """
        times = self.cache.incr()
        self.cache.update_expiration()
        return times
