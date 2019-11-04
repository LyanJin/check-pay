import json

import requests

from app.docs.doc_gateway.gateway_config import GatewayResponseConfig
from app.docs.doc_gateway.gateway_deposit import GatewayResponseDeposit
from app.enums.trade import PaymentTypeEnum
from app.logics.gateway.sign_check import GatewaySign
from config import MerchantEnum
from scripts.init_data import InitData, DateTimeKit
from tests import TestGatewayBase
from contextlib import contextmanager


class TestCallBackApi(TestGatewayBase):

    @contextmanager
    def with_client(self):
        with self.app.test_client() as client:
            # 临时保存
            self.client_ctx = client
            yield
            # 用完清除
            self.client_ctx = None

    def test_gateway_api(self):
        with self.with_client():
            merchant = MerchantEnum.TEST_API
            InitData.merchant = merchant
            InitData.init_sample_data()
            self.__test_get_config(merchant)
            # self.__test_deposit(merchant)

    def __test_get_config(self, merchant):
        self.path = "/config/get"
        post_data = dict(
            merchant_id=merchant.value,
            user_ip="127.0.0.1"
        )

        post_data['sign'] = GatewaySign(merchant).generate_sign(post_data)
        post_data['user_id'] = '1000000'

        rsp = self.do_request(post_data)
        self.assertEqual(200, rsp.status_code)
        self.assertEqual(GatewayResponseConfig.error_code, rsp.json['error_code'], rsp.json['message'])

        payment_types = rsp.json['data']['payment_types']
        self.assertIsInstance(payment_types, (list,))
        item = payment_types[0]
        self.assertEqual(InitData.channel_enum.conf.payment_type, PaymentTypeEnum.from_name(item['name']))
        print('payment_types:', payment_types)

    def __test_deposit(self, merchant):
        self.path = "/deposit/request"
        post_data = dict(
            merchant_id=merchant.value,
            user_id="100",
            amount="1239.45",
            mch_tx_id="22349813471982341",
            create_time=DateTimeKit.get_cur_timestamp(),
            payment_type=InitData.channel_enum.conf.payment_type.name,
            user_ip="192.168.1.1",
            notify_url="https://google.com",
        )
        print('post_data:', post_data)

        post_data['sign'] = GatewaySign(merchant).generate_sign(post_data)
        post_data['redirect_url'] = "https://google.com"
        post_data['extra'] = json.dumps(dict(x=1, y=2))

        print('post_data:', post_data)

        rsp = self.do_request(post_data)
        self.assertEqual(200, rsp.status_code)
        self.assertEqual(GatewayResponseDeposit.error_code, rsp.json['error_code'])
        print(rsp.json['data'])

        rsp = requests.get(rsp.json['data']['redirect_url'])
        # rsp = self.client_ctx.get(rsp.json['data']['redirect_url'])
        self.assertEqual(200, rsp.status_code)
        print(rsp.text)
        # print(rsp.data.decode('utf8'))
