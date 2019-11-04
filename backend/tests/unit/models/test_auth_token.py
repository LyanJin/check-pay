import base64
import time

from app.caches.auth_code import UserLoginCache
from app.libs.error_code import TokenBadError, TokenExpiredError, LoginOtherError
from app.logics.token.token_base import UserLoginToken
from app.models.user import User
from config import MerchantEnum
from tests import TestCashierUnitBase


class TestAuthToekn(TestCashierUnitBase):
    ENABLE_PRINT = False
    ENABLE_SQL_LOG = False

    def test_auth_token(self):
        uid = 1000

        token = UserLoginToken.generate_token(uid=uid, mch_name=MerchantEnum.TEST.name)

        # ttl = UserLoginCache(uid).get_ttl()
        # self.assert_(ttl >= TOKEN_EXPIRATION - 1)
        # self.assert_(ttl <= TOKEN_EXPIRATION)

        cache_data = UserLoginCache(uid).loads()
        # self.assertEqual(cache_data['time'], login_time)
        self.assertEqual(cache_data['ip'], '127.0.0.1')

        user = UserLoginToken.verify_token(token)
        self.assertEqual(user['uid'], uid)

    def test_bad_token(self):
        ret = UserLoginToken.verify_token('')
        self.assertIsInstance(ret, TokenBadError)
        ret = UserLoginToken.verify_token('xxxxxx')
        self.assertIsInstance(ret, TokenBadError)
        ret = UserLoginToken.verify_token(
            base64.b64encode('sdsadfasfdsalkasdlkjsdalasdjksa'.encode('utf8')).decode('utf8')
        )
        self.assertIsInstance(ret, TokenBadError)

    def x_expired_token(self):
        uid = 1000

        token = UserLoginToken.generate_token(uid=uid, mch_name=MerchantEnum.TEST.name)
        time.sleep(2)
        ret = UserLoginToken.verify_token(token)
        self.assertIsInstance(ret, TokenExpiredError)

        token = UserLoginToken.generate_token(uid=uid, mch_name=MerchantEnum.TEST.name)
        UserLoginCache(uid).delete_cache()
        ret = UserLoginToken.verify_token(token)
        self.assertIsInstance(ret, TokenExpiredError)

    def test_other_login(self):
        uid = 1000

        token = UserLoginToken.generate_token(uid=uid, mch_name=MerchantEnum.TEST.name)

        cache_data = UserLoginCache(uid).loads()
        UserLoginCache(uid).dumps(dict(
            time=cache_data['time'] - 1,
            ip=cache_data['ip'],
            mch_name=MerchantEnum.TEST.name,
        ))

        ret = UserLoginToken.verify_token(token)
        self.assertIsInstance(ret, LoginOtherError)
