from decimal import Decimal

from app.enums.account import AccountTypeEnum
from app.enums.channel import ChannelStateEnum, ChannelConfigEnum
from app.enums.trade import PaymentFeeTypeEnum, OrderSourceEnum, InterfaceTypeEnum, PayMethodEnum, PayTypeEnum, \
    SettleTypeEnum
from app.libs.datetime_kit import DateTimeKit
from app.logics.channel.chanel_cache import ChannelLimitCacheCtl
from app.logics.order.create_ctl import OrderCreateCtl
from app.channel.ponypay.deposit.callback import CallbackPonypay
from app.channel.ponypay.withdraw.callback import WithdrawCallbackPonypay
from app.models.channel import ChannelConfig
from app.models.merchant import MerchantFeeConfig, MerchantInfo
from app.models.user import User
from config import MerchantEnum, MerchantTypeEnum
from scripts.init_data import InitData
from tests import TestCallBackBase
from contextlib import contextmanager


class TestCallBackApi(TestCallBackBase):

    @contextmanager
    def with_client(self):
        with self.app.test_client() as client:
            # 临时保存
            self.client_ctx = client
            yield
            # 用完清除
            self.client_ctx = None

    def test_callback_api(self):
        with self.with_client():
            self.__test_callback_ponypay()

    def __test_callback_ponypay(self):
        # self.__test_callback_ponypay_deposit()
        self.__test_callback_ponypay_withdraw()

    def __test_callback_ponypay_withdraw(self):
        InitData.init_sample_data()
        self.__test_withdraw_callback_success()
        self.__test_withdraw_callback_fail()

    def __test_withdraw_callback_success(self):
        self.do_ponypay_withdraw_callback('1')

    def __test_withdraw_callback_fail(self):
        self.do_ponypay_withdraw_callback('0')

    def do_ponypay_withdraw_callback(self, status):
        amount = tx_amount = Decimal("100.25")

        # 生成一个可以回调的订单
        order = InitData.init_withdraw_order_deal(amount)

        channel_config = ChannelConfig.query_by_channel_id(order.channel_id)
        controller = WithdrawCallbackPonypay(channel_config.channel_enum)
        sign = controller.generate_sign(order.sys_tx_id, tx_amount)

        self.path = "/callback/ponypay/withdraw"
        params = """merchant_id={}&corderid={}&money={}&status={}&sign={}""".format(
            controller.third_config['mch_id'],
            order.sys_tx_id,
            tx_amount,
            status,
            sign,
        )
        response = self.do_get_request(params=params)
        self.assertEqual(200, response.status_code)
        self.assertEqual("SUCCESS", response.data.decode("utf-8"))

    def __test_callback_ponypay_deposit(self):
        self.path = "/callback/ponypay/deposit"

        # 初始化数据
        kwargs = dict(
            fee="2.5",
            fee_type=PaymentFeeTypeEnum.PERCENT_PER_ORDER,
            limit_per_min="200",
            limit_per_max="10000",
            trade_begin_hour="00",
            trade_begin_minute="00",
            trade_end_hour="23",
            trade_end_minute="59",
            maintain_begin=DateTimeKit.str_to_datetime("2019-09-07 09:00:00"),
            maintain_end=DateTimeKit.str_to_datetime("2019-09-07 09:00:00"),
            settlement_type=SettleTypeEnum.D0,
            state=ChannelStateEnum.TESTING,
            priority="101"
        )
        rst, error = ChannelConfig.update_channel(ChannelConfigEnum.CHANNEL_1001, **kwargs)
        self.assertEqual(rst, True)
        self.assertEqual(error, None)
        # ChannelLimitCacheCtl(PayTypeEnum.DEPOSIT).sync_db_channels_to_cache()

        merchant = MerchantEnum.TEST
        merchant_fee_list = [
            dict(
                merchant=merchant,
                payment_way=PayTypeEnum.DEPOSIT,
                value="3",
                fee_type=PaymentFeeTypeEnum.PERCENT_PER_ORDER,
                payment_method=PayMethodEnum.ZHIFUBAO_SAOMA
            ),
            dict(
                merchant=merchant,
                payment_way=PayTypeEnum.WITHDRAW,
                value="3.2",
                fee_type=PaymentFeeTypeEnum.PERCENT_PER_ORDER
            )
        ]

        ret, error = MerchantFeeConfig.update_fee_config(merchant, merchant_fee_list)
        self.assertEqual(rst, True)
        self.assertEqual(error, None)

        info = dict(
            account="+8618977772222",
            merchant=MerchantEnum.TEST,
            ac_type=AccountTypeEnum.MOBILE,
            login_pwd="123456789",
        )
        MerchantInfo.create_merchant(MerchantEnum.TEST, MerchantTypeEnum.TEST)
        user = User.register_account(merchant=info['merchant'], account=info['account'], ac_type=info['ac_type'],
                                     login_pwd=info['login_pwd'])

        uid = user.id
        channel_config = ChannelConfig.query_latest_one(query_fields=dict(channel_enum=ChannelConfigEnum.CHANNEL_1001))
        channel_conf = ChannelConfigEnum.CHANNEL_1001.conf
        channel_conf['white_ip'].append("127.0.0.1")
        merchant_fee = MerchantFeeConfig.query_latest_one(query_fields=dict(
            merchant=MerchantEnum.TEST,
            payment_way=PayTypeEnum.DEPOSIT,
            payment_method=channel_conf.payment_method
        ))

        self.__test_callback_order_success(uid, channel_config, merchant_fee, '1')
        self.__test_callback_order_success(uid, channel_config, merchant_fee, '-1')

        stop = 1

    def __test_callback_order_success(self, uid, channel_config, merchant_fee, status):
        amount = "400.00"
        money = "399.99"
        kwargs = dict(
            uid=uid,
            merchant=MerchantEnum.TEST,
            amount=amount,
            channel_id=channel_config.channel_id,
            mch_fee_id=merchant_fee.config_id,
            order_type=PayTypeEnum.DEPOSIT,
            source=OrderSourceEnum.TESTING,
            in_type=InterfaceTypeEnum.CASHIER_H5,
        )
        order, ref_id = OrderCreateCtl.create_order_event(**kwargs)
        self.do_ponypay_order_callback(order.sys_tx_id, status=status, money=money)

        # TODO: 检查数据库数据是否修改正确

    def do_ponypay_order_callback(self, orderid, status="1", money="350"):
        porder = "4288969"
        merchant_id = CallbackPonypay.third_config['mch_id']
        paytype = "ZFB"
        sign = CallbackPonypay.generate_sign(merchant_id, orderid, money)
        params = """porder={}&merchant_id={}&money={}&orderid={}&status={}&paytype={}&sign={}""".format(
            porder,
            merchant_id,
            money,
            orderid,
            status,
            paytype,
            sign,
        )
        response = self.do_get_request(params=params)
        self.assertEqual(200, response.status_code)
        self.assertEqual("SUCCESS", response.data.decode("utf-8"))
