import logging
from unittest import TestCase
from urllib.parse import urlencode

from flask_testing import LiveServerTestCase

from app.app import FlaskApp
from app.extensions import redis, db
from config import MerchantEnum


class TestCaseMixin(object):
    ENABLE_PRINT = False

    def print(self, *args, **kwargs):
        if self.ENABLE_PRINT:
            print(*args, **kwargs)


class TestNoneAppBase(TestCaseMixin, TestCase):
    """
    非app相关的测试,不需要发送http请求的
    """
    pass


class TestAppBase(TestCaseMixin, LiveServerTestCase):
    """
    App相关的测试
    """

    client_ctx = None
    path = '/'
    url_prefix = "/api/"

    # 是否打印sql log
    ENABLE_SQL_LOG = False

    token = None

    t_merchant = MerchantEnum.TEST

    def create_app(self):
        raise NotImplemented

    def get_headers(self):
        if not self.token:
            return dict()

        return {
            'Authorization': "Bearer " + self.token,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def do_request(self, json_data=None, path=None):
        _path = (path or self.path).strip('/')
        url_path = '/'.join([self.url_prefix, _path])
        url = self.get_server_url() + url_path
        # print('post to: %s, data: %s' % (url, json_data))

        headers = self.get_headers()
        return self.client_ctx.post(url, json=json_data, headers=headers)

    def do_get_request(self, params):
        if isinstance(params, (dict, )):
            params = urlencode(params)
        url = "".join([self.get_server_url(), self.url_prefix, self.path])
        # url = "http://127.0.0.1:5000/api/callback/v1/callback/ponypay/deposit"
        return self.client_ctx.get(url + "?" + params)

    @staticmethod
    def __clear_cache():
        for k in redis.keys():
            redis.delete(k)

    def setUp(self) -> None:

        if self.ENABLE_SQL_LOG:
            logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

        db.create_all()
        self.__clear_cache()

    def tearDown(self) -> None:
        db.drop_all()
        self.__clear_cache()


class TestCashierBase(TestAppBase):
    url_prefix = "/api/cashier/v1"

    def create_app(self):
        app = FlaskApp.create_app('cashier', 'development')
        return app


class TestCallBackBase(TestAppBase):
    url_prefix = "/api/callback/v1"

    def create_app(self):
        app = FlaskApp.create_app('callback', 'development')
        return app


class TestBackofficeBase(TestAppBase):
    url_prefix = "/api/backoffice/v1"

    def create_app(self):
        app = FlaskApp.create_app('backoffice', 'development')
        return app


class TestGatewayBase(TestAppBase):
    url_prefix = "/api/gateway/v1"

    def create_app(self):
        app = FlaskApp.create_app('gateway', 'development')
        return app


class TestCashierUnitBase(TestAppBase):

    def create_app(self):
        app = FlaskApp.create_app('cashier', 'development')
        return app


class TestBackofficeUnitBase(TestAppBase):

    def create_app(self):
        app = FlaskApp.create_app('backoffice', 'development')
        return app
