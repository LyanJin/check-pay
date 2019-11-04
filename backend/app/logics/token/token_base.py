import base64

from flask import current_app
from itsdangerous import JSONWebSignatureSerializer, BadSignature

from app.caches.admin_auth import AdminLoginCache
from app.caches.auth_code import UserLoginCache
from app.caches.merchant_auth import MerchantLoginCache
from app.libs.datetime_kit import DateTimeKit
from app.libs.error_code import TokenBadError, TokenExpiredError, LoginOtherError
from app.libs.ip_kit import IpKit

DEBUG_LOG = False


class LoginToken:
    cache_cls = None

    @classmethod
    def generate_token(cls, uid, **kwargs):
        """
        生成token
        :param uid:
        :return: 返回一个已经进行base64编码的token字符串
        """
        s = JSONWebSignatureSerializer(current_app.config['SECRET_KEY'])

        login_time = DateTimeKit.get_cur_timestamp(1000)

        data = dict(
            uid=uid,
            time=login_time,
            ip=IpKit.get_remote_ip(),
        )
        data.update(kwargs)

        # 缓存登录状态
        cache = cls.cache_cls(uid)
        cache.dumps(data)

        token = s.dumps(data)
        b64_token = base64.b64encode(token).decode('utf8')

        DEBUG_LOG and current_app.logger.debug('token generated, key: %s, ttl: %s, data: %s, token: %s, b64_token: %s',
                                               cache.get_cache_key(), cache.get_ttl(), data, token, b64_token)

        return b64_token

    @classmethod
    def verify_token(cls, b64_token):
        """
        验证token
        :param b64_token: 已经被base64编码的字符串
        :return: (user, error)
        """
        if not b64_token:
            # current_app.config['SENTRY_DSN'] and current_app.logger.error('TokenBadError, b64_token: %s', b64_token)
            return TokenBadError()

        try:
            # 先进行base64解码
            token = base64.b64decode(b64_token)
        except:
            # current_app.config['SENTRY_DSN'] and current_app.logger.error('TokenBadError, b64_token: %s', b64_token)
            return TokenBadError()

        s = JSONWebSignatureSerializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except BadSignature:
            # current_app.config['SENTRY_DSN'] and current_app.logger.error('TokenBadError, token: %s', token)
            return TokenBadError()

        # 缓存过期即token过期
        cache = cls.cache_cls(data['uid'])

        cache_data = cache.loads()
        if not cache_data:
            # current_app.config['SENTRY_DSN'] and current_app.logger.error('TokenExpiredError, token: %s, data: %s', token, data)
            return TokenExpiredError()

        # 异地登录处理
        if cache_data != data:
            message = LoginOtherError.message.format(cache_data['ip'])
            # current_app.config['SENTRY_DSN'] and current_app.logger.error('LoginOtherError, token: %s, data: %s', token, data)
            return LoginOtherError(message=message)

        # 更新缓存有效时间
        cache.update_expiration()

        DEBUG_LOG and current_app.logger.info('update ttl, key: %s, ttl: %s', cache.get_cache_key(), cache.get_ttl())

        return data

    @classmethod
    def remove_token(cls, uid):
        """
        删除token
        :param uid:
        :return:
        """
        cache = cls.cache_cls(uid)
        cache.delete()

        DEBUG_LOG and current_app.logger.info('remove token, key: %s, result: %s',
                                              cache.get_cache_key(), 'ok' if not cache.loads() else 'failed')

    @classmethod
    def update_expiration(cls, uid):
        """
        更新token有效时间
        :param uid:
        :return:
        """
        cls.cache_cls(uid).update_expiration()


class AdminLoginToken(LoginToken):
    cache_cls = AdminLoginCache


class UserLoginToken(LoginToken):
    cache_cls = UserLoginCache


class MerchantLoginToken(LoginToken):
    cache_cls = MerchantLoginCache
