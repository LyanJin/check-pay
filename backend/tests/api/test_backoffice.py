import hashlib
from contextlib import contextmanager
from decimal import Decimal

from app.docs.doc_internal.trade_manage import WithdrawBankEntryResult
from app.enums.channel import ChannelConfigEnum, ChannelStateEnum
from app.libs.api_exception import APIException
from app.libs.balance_kit import BalanceKit
from app.libs.datetime_kit import DateTimeKit, DateTimeFormatEnum
from app.logics.order.create_ctl import OrderCreateCtl
from app.logics.token.admin_token import AdminLoginToken
from app.models.bankcard import BankCard
from app.models.order.order import OrderWithdraw
from app.models.order.order_event import OrderEvent
from config import MerchantTypeEnum
from app.enums.trade import PayMethodEnum, PaymentFeeTypeEnum, PaymentBankEnum, PayTypeEnum, OrderSourceEnum, \
    PaymentTypeEnum, InterfaceTypeEnum, OrderStateEnum, CostTypeEnum
from app.enums.balance import ManualAdjustmentType
from app.libs.error_code import ResponseSuccess, ParameterException, MerchantUpdateError, SqlIntegrityError, \
    TokenBadError, TokenExpiredError, PerLimitMustLittleDayLimitError
from app.models.merchant import MerchantInfo, MerchantFeeConfig
from config import MerchantEnum
from scripts.order_mix import OrderMixes
from tests import TestBackofficeBase
from app.libs.error_code import LoginPasswordError, LoginAccountError, DateStartMoreThanError, DataStartMoreThanError
from app.models.backoffice.admin_user import AdminUser
from app.models.channel import ProxyChannelConfig, ChannelRouter, ChannelConfig


class TestBackofficeApi(TestBackofficeBase):

    @contextmanager
    def with_client(self):
        with self.app.test_client() as client:
            # 临时保存
            self.client_ctx = client
            yield
            # 用完清除
            self.client_ctx = None

    def test_backoffice_api(self):
        with self.with_client():
            # 准备测试数据
            data = dict(
                merchant=MerchantEnum.TEST.name,
                account='clark',
                account_err='clark_1',
                password=hashlib.md5('12Lk-M_6mn7'.encode('utf8')).hexdigest(),
                password_err=hashlib.md5('12Lk-Mse34'.encode('utf8')).hexdigest(),
            )

            self.__register_account(data)
            #
            self.__test_admin_token_auth(data)
            #
            self.__test_api_auth_account_login(data)
            #
            self.__test_api_merchant_fee()
            #
            self.__test_api_merchant_balance()
            #
            self.__test_api_channel()
            # 测试路由
            self.__test_router_list()
            # 提款
            self.__test_api_withdraw()
            # 最后登出
            self.__test_api_account_logout()

    def __test_api_account_logout(self):
        """
        登出测试
        :return:
        """
        self.path = '/auth/account/logout'
        response = self.do_request()
        self.assertEqual(ResponseSuccess.code, response.status_code)
        self.assertEqual(ResponseSuccess.error_code, response.json['error_code'], response.json['message'])

        rst = AdminLoginToken.verify_token(self.token)
        self.assertIsInstance(rst, (TokenExpiredError,))

    def __register_account(self, data):
        # 先往数据库生成一个账号
        AdminUser.register_account(account=data['account'], login_pwd=data['password'])
        if not MerchantInfo.query_merchant(MerchantEnum.TEST):
            MerchantInfo.create_merchant(m_name=MerchantEnum.TEST, m_type=MerchantTypeEnum.TEST)

    def __test_admin_token_auth(self, data):
        self.path = '/merchant/balance/edit'

        user = AdminUser.query_user(account=data['account'])

        # 测试没有token
        post_data = dict(
            name=MerchantEnum.TEST.name,
            adjustment_type=ManualAdjustmentType.MINUS.name,
            amount="200.34",
            reason="因为要改，所有就改了",
        )
        response = self.do_request(post_data)
        self.assertEqual(TokenBadError.code, response.status_code, response.json['message'])
        self.assertEqual(TokenBadError.error_code, response.json['error_code'], response.json['message'])

        # 测试token错误
        response = self.do_request(post_data)
        self.assertEqual(TokenBadError.code, response.status_code, response.json['message'])
        self.assertEqual(TokenBadError.error_code, response.json['error_code'], response.json['message'])

        # 生成token
        self.token = AdminLoginToken.generate_token(user.uid)
        # 验证token
        rst = AdminLoginToken.verify_token(self.token)
        self.assertNotIsInstance(rst, (APIException,))

        # 测试token验证通过
        response = self.do_request(post_data)
        self.assertEqual(MerchantUpdateError.code, response.status_code, response.json['message'])
        self.assertEqual(MerchantUpdateError.error_code, response.json['error_code'], response.json['message'])

        AdminLoginToken.remove_token(user.uid)

        # token被删除，验证失败
        response = self.do_request(post_data)
        self.assertEqual(TokenExpiredError.code, response.status_code, response.json['message'])
        self.assertEqual(TokenExpiredError.error_code, response.json['error_code'], response.json['message'])

    def __test_api_merchant_balance(self):
        self.path = '/merchant/balance/edit'

        post_data = dict(
            name='XXXXX',
            adjustment_type=ManualAdjustmentType.MINUS.name,
            amount="500.34",
            reason="因为要改，所有就改了",
        )
        response = self.do_request(post_data)
        self.assertEqual(ParameterException.code, response.status_code, response.json['message'])
        self.assertEqual(ParameterException.error_code, response.json['error_code'], response.json['message'])
        self.assertTrue("无效的商户名称" in response.json['message'])

        post_data = dict(
            name=MerchantEnum.QF3.name,
            adjustment_type=ManualAdjustmentType.MINUS.name,
            amount="500.34",
            reason="因为要改，所有就改了",
        )
        response = self.do_request(post_data)
        self.assertEqual(ParameterException.code, response.status_code, response.json['message'])
        self.assertEqual(ParameterException.error_code, response.json['error_code'], response.json['message'])
        self.assertTrue("未创建的商户" in response.json['message'])

        # # 创建TEST商户
        # merchant = MerchantInfo.create_merchant(MerchantEnum.TEST, MerchantTypeEnum.TEST)
        # self.assertEqual(merchant.id, 1)
        # self.assertEqual(merchant.mch_name, MerchantEnum.TEST)
        # self.assertEqual(merchant.m_type, MerchantTypeEnum.TEST)
        # self.assertEqual(merchant.state, AccountStateEnum.ACTIVE)
        # self.assertEqual(merchant.balance_total, 0)

        post_data = dict(
            name=MerchantEnum.TEST.name,
            adjustment_type='XXXXX',
            amount="500.34",
            reason="因为要改，所有就改了",
        )
        response = self.do_request(post_data)
        self.assertEqual(ParameterException.code, response.status_code, response.json['message'])
        self.assertEqual(ParameterException.error_code, response.json['error_code'], response.json['message'])
        self.assertTrue("无效的调整类型" in response.json['message'])

        post_data = dict(
            name=MerchantEnum.TEST.name,
            adjustment_type=ManualAdjustmentType.MINUS.name,
            amount="500.x4",
            reason="因为要改，所有就改了",
        )
        response = self.do_request(post_data)
        self.assertEqual(ParameterException.code, response.status_code, response.json['message'])
        self.assertEqual(ParameterException.error_code, response.json['error_code'], response.json['message'])
        self.assertTrue("无效的金额" in response.json['message'])

        # 余额不足，减失败
        post_data = dict(
            name=MerchantEnum.TEST.name,
            adjustment_type=ManualAdjustmentType.MINUS.name,
            amount="500.34",
            reason="因为要改，所有就改了",
        )
        response = self.do_request(post_data)
        self.assertEqual(MerchantUpdateError.code, response.status_code, response.json['message'])
        self.assertEqual(MerchantUpdateError.error_code, response.json['error_code'], response.json['message'])
        self.assertTrue("可用余额不足" in response.json['message'])

        # 增加余额
        post_data = dict(
            name=MerchantEnum.TEST.name,
            adjustment_type=ManualAdjustmentType.PLUS.name,
            amount="500.34",
            reason="因为要改，所有就改了",
        )
        response = self.do_request(post_data)
        self.assertEqual(ResponseSuccess.code, response.status_code, response.json['message'])
        self.assertEqual(ResponseSuccess.error_code, response.json['error_code'], response.json['message'])
        self.assertTrue(ResponseSuccess.message == response.json['message'])

        merchant = MerchantInfo.query_merchant(MerchantEnum.TEST)
        self.assertEqual(merchant.balance_available, Decimal("500.34"))
        self.assertEqual(merchant.balance_total, Decimal("500.34"))

        # 可用余额够了，减成功
        post_data = dict(
            name=MerchantEnum.TEST.name,
            adjustment_type=ManualAdjustmentType.MINUS.name,
            amount="100.01",
            reason="因为要改，所有就改了",
        )
        response = self.do_request(post_data)
        self.assertEqual(ResponseSuccess.code, response.status_code, response.json['message'])
        self.assertEqual(ResponseSuccess.error_code, response.json['error_code'], response.json['message'])
        self.assertTrue(ResponseSuccess.message == response.json['message'])

        merchant = MerchantInfo.query_merchant(MerchantEnum.TEST)
        self.assertEqual(merchant.balance_available, Decimal("400.33"))
        self.assertEqual(merchant.balance_total, Decimal("400.33"))

        # 可用余额不足，冻结失败
        post_data = dict(
            name=MerchantEnum.TEST.name,
            adjustment_type=ManualAdjustmentType.FROZEN.name,
            amount="500.01",
            reason="因为要改，所有就改了",
        )
        response = self.do_request(post_data)
        self.assertEqual(MerchantUpdateError.code, response.status_code, response.json['message'])
        self.assertEqual(MerchantUpdateError.error_code, response.json['error_code'], response.json['message'])
        self.assertTrue("可用余额不足" in response.json['message'])

        merchant = MerchantInfo.query_merchant(MerchantEnum.TEST)
        self.assertEqual(merchant.balance_available, Decimal("400.33"))
        self.assertEqual(merchant.balance_total, Decimal("400.33"))

        # 可用余额够了，冻结成功
        post_data = dict(
            name=MerchantEnum.TEST.name,
            adjustment_type=ManualAdjustmentType.FROZEN.name,
            amount="100.01",
            reason="因为要改，所有就改了",
        )
        response = self.do_request(post_data)
        self.assertEqual(ResponseSuccess.code, response.status_code, response.json['message'])
        self.assertEqual(ResponseSuccess.error_code, response.json['error_code'], response.json['message'])
        self.assertTrue(ResponseSuccess.message == response.json['message'])

        merchant = MerchantInfo.query_merchant(MerchantEnum.TEST)
        self.assertEqual(merchant.balance_available, Decimal("300.32"))
        self.assertEqual(merchant.balance_frozen, Decimal("100.01"))
        self.assertEqual(merchant.balance_total, Decimal("400.33"))

        # 冻结余额不足，解冻失败
        post_data = dict(
            name=MerchantEnum.TEST.name,
            adjustment_type=ManualAdjustmentType.UNFROZEN.name,
            amount="200.01",
            reason="因为要改，所有就改了",
        )
        response = self.do_request(post_data)
        self.assertEqual(MerchantUpdateError.code, response.status_code, response.json['message'])
        self.assertEqual(MerchantUpdateError.error_code, response.json['error_code'], response.json['message'])
        self.assertTrue("冻结余额不足" in response.json['message'])

        merchant = MerchantInfo.query_merchant(MerchantEnum.TEST)
        self.assertEqual(merchant.balance_available, Decimal("300.32"))
        self.assertEqual(merchant.balance_frozen, Decimal("100.01"))
        self.assertEqual(merchant.balance_total, Decimal("400.33"))

        # 冻结余额不足，解冻失败
        post_data = dict(
            name=MerchantEnum.TEST.name,
            adjustment_type=ManualAdjustmentType.UNFROZEN.name,
            amount="50.01",
            reason="因为要改，所有就改了",
        )
        response = self.do_request(post_data)
        self.assertEqual(ResponseSuccess.code, response.status_code, response.json['message'])
        self.assertEqual(ResponseSuccess.error_code, response.json['error_code'], response.json['message'])
        self.assertTrue(ResponseSuccess.message == response.json['message'])

        merchant = MerchantInfo.query_merchant(MerchantEnum.TEST)
        self.assertEqual(merchant.balance_available, Decimal("350.33"))
        self.assertEqual(merchant.balance_frozen, Decimal("50.00"))
        self.assertEqual(merchant.balance_total, Decimal("400.33"))

        # 在途余额不足，扣减失败
        post_data = dict(
            name=MerchantEnum.TEST.name,
            adjustment_type=ManualAdjustmentType.MINUS_INCOME.name,
            amount="200.01",
            reason="因为要改，所有就改了",
        )
        response = self.do_request(post_data)
        self.assertEqual(MerchantUpdateError.code, response.status_code, response.json['message'])
        self.assertEqual(MerchantUpdateError.error_code, response.json['error_code'], response.json['message'])
        self.assertTrue("在途余额不足" in response.json['message'])

        merchant = MerchantInfo.query_merchant(MerchantEnum.TEST)
        self.assertEqual(merchant.balance_available, Decimal("350.33"))
        self.assertEqual(merchant.balance_frozen, Decimal("50.00"))
        self.assertEqual(merchant.balance_income, 0)
        self.assertEqual(merchant.balance_total, Decimal("400.33"))

    def __test_api_merchant_fee(self):
        # 先删除所有商户
        MerchantInfo.delete_all()

        r1 = dict(
            name=PayMethodEnum.WEIXIN_TO_BANK.value,
            value="3.2",
            fee_type=PaymentFeeTypeEnum.PERCENT_PER_ORDER.value
        )
        r2 = dict(
            name=PayMethodEnum.BANK_TO_BANK.value,
            value="4.45",
            fee_type=PaymentFeeTypeEnum.PERCENT_PER_ORDER.value
        )
        w1 = dict(
            value='3.3',
            fee_type=PaymentFeeTypeEnum.YUAN_PER_ORDER.value,
            cost_type=CostTypeEnum.MERCHANT.name,
        )
        post_data = dict(
            name=MerchantEnum.TEST.name,
            type=MerchantTypeEnum.TEST.value,
            deposit_info=[r1, r2],
            withdraw_info=w1
        )

        # 新建商户费率
        self.path = '/merchant/fee/add'

        # 新建商户费率成功
        response = self.do_request(post_data)
        self.assertEqual(response.status_code, ResponseSuccess.code)
        self.assertEqual(response.json['error_code'], ResponseSuccess.error_code, response.json['message'])

        # 新建商户费率 商户名重复
        response = self.do_request(post_data)
        self.assertEqual(response.status_code, SqlIntegrityError.code)
        self.assertEqual(response.json['error_code'], SqlIntegrityError.error_code, response.json['message'])

        # 费率编辑
        self.path = '/merchant/fee/edit'
        r1 = dict(
            name=PayMethodEnum.WEIXIN_SAOMA.value,
            value="0.2",
            fee_type=PaymentFeeTypeEnum.PERCENT_PER_ORDER.value
        )
        edit_post_data = dict(
            name='Test',
            deposit_info=[r1, r2],
            withdraw_info=w1
        )

        response = self.do_request(edit_post_data)
        self.assertEqual(ResponseSuccess.code, response.status_code, response.json['message'])
        self.assertEqual(ResponseSuccess.error_code, response.json['error_code'], response.json['message'])

    def __test_api_auth_account_login(self, data):
        # 测试登陆接口
        self.path = '/auth/account/login'

        # 测试登陆成功
        post_data = dict(account=data['account'], password=data['password'])
        response = self.do_request(post_data)
        self.assertEqual(response.status_code, ResponseSuccess.code)

        # 记录好token
        self.token = response.json['data']['token']

        # 测试用户名不存在
        post_data = dict(account=data['account_err'], password=data['password'])
        response = self.do_request(post_data)
        self.assertEqual(response.status_code, LoginAccountError.code)
        self.assertEqual(response.json['error_code'], LoginAccountError.error_code)

        # 测试密码错误
        post_data = dict(account=data['account'], password=data['password_err'])
        response = self.do_request(post_data)
        self.assertEqual(response.status_code, LoginPasswordError.code)
        self.assertEqual(response.json['error_code'], LoginPasswordError.error_code)

    def __test_api_channel(self):
        # 充值通道管理 新增通道
        channel_enum = ChannelConfigEnum.CHANNEL_1001
        post_data = dict(
            channel_id=channel_enum.value,
            fee="2.3",
            fee_type="1",
            limit_per_min="2000",
            limit_per_max="50000",
            limit_day_max="50000",
            start_time="09:00",
            end_time="23:59",
            state="10",
            settlement_type="1",
            priority="1"
        )

        post_data["state"] = 10
        # 数值型参数类型错误
        self.path = '/channel/deposit/add'

        response = self.do_request(post_data)
        self.assertEqual(response.status_code, ParameterException.code)
        self.assertEqual(response.json['error_code'], ParameterException.error_code)
        # print(response.json['message'], "this field must be String type")
        post_data["state"] = "10"

        # 测试交易日期为空的情况
        response = self.do_request(post_data)
        print(response.json)
        self.assertEqual(ResponseSuccess.code, response.status_code, response.json['message'])
        self.assertEqual(ResponseSuccess.error_code, response.json['error_code'], response.json['message'])
        # print(response.json['message'], "this field must be String type")
        post_data['maintain_begin'] = "2019-09-27 09:10:00"
        post_data['maintain_end'] = "2019-10-20 23:09:00"

        # 测试每笔交易上限大于日交易上限
        post_data['limit_day_max'] = "40000"
        response = self.do_request(post_data)
        print(response.json)
        self.assertEqual(PerLimitMustLittleDayLimitError.code, response.status_code)
        self.assertEqual(PerLimitMustLittleDayLimitError.error_code, response.json['error_code'])
        # print(response.json['message'], "this field must be String type")
        # self.assertEqual(response.json['message'], "单笔交易最大值必须小于当日交易限额")
        post_data['limit_day_max'] = "60000"

        # 时间类型参数业务数据不对
        post_data["maintain_begin"] = "2020-08-23 09:30:00"
        response = self.do_request(post_data)
        self.assertEqual(response.status_code, DateStartMoreThanError.code)
        self.assertEqual(response.json['error_code'], DateStartMoreThanError.error_code)
        self.assertEqual(response.json['message'], DateStartMoreThanError.message)
        post_data["maintain_begin"] = "2019-09-27 09:00:00"

        # 业务类型数据不对
        post_data["limit_per_min"] = "100000"
        response = self.do_request(post_data)
        self.assertEqual(response.status_code, DataStartMoreThanError.code)
        self.assertEqual(response.json['error_code'], DataStartMoreThanError.error_code)
        self.assertEqual(response.json['message'], DataStartMoreThanError.message)
        post_data["limit_per_min"] = "2000"

        # 时间类型数据格式错误
        post_data["maintain_begin"] = "2019/09/27 09:00:00"
        response = self.do_request(post_data)
        self.assertEqual(response.status_code, ParameterException.code)
        self.assertEqual(response.json['error_code'], ParameterException.error_code)
        # self.assertEqual(response.json['message'], "无效的时间格式")
        post_data["maintain_begin"] = "2019-09-27 09:00:00"

        # 测试成功添加数据
        response = self.do_request(post_data)
        self.assertEqual(response.status_code, ResponseSuccess.code)
        channel = ChannelConfig.query_latest_one(dict(channel_enum=channel_enum))
        self.assertEqual(channel.channel_enum.value, post_data['channel_id'])
        self.assertEqual(channel.settlement_type.value, int(post_data['settlement_type']))

        # 渠道管理：编辑通道

        self.path = '/channel/deposit/edit'
        post_data['settlement_type'] = '3'
        response = self.do_request(post_data)
        self.assertEqual(response.status_code, ResponseSuccess.code)
        channel = ChannelConfig.query_latest_one(dict(channel_enum=channel_enum))
        self.assertEqual(channel.channel_enum.value, post_data['channel_id'])
        self.assertEqual(channel.settlement_type.value, 3)

        # 测试 不支持的 枚举类型数据
        self.path = '/channel/deposit/edit'
        post_data['state'] = '110'
        response = self.do_request(post_data)
        self.assertEqual(response.status_code, ParameterException.code)
        self.assertEqual(response.json['error_code'], ParameterException.error_code)
        # self.assertEqual(response.json['message'], "无效的通道状态")
        post_data['state'] = "10"

        # 代付通道管理： 新增代付通道

        self.path = "/channel/withdraw/add"
        withdraw_postdata = dict(
            channel_id=channel_enum.value,
            fee="2.3",
            fee_type="1",
            limit_per_min="2000",
            limit_per_max="50000",
            limit_day_max="50000",
            start_time="09:00",
            end_time="23:59",
            maintain_begin="2019-09-27 09:00:00",
            maintain_end="2019-10-20 23:00:00",
            state="10",
            banks=["1", "2", "4", "6", "3", "5", "15"]
        )

        # 测试参数类型错误
        withdraw_postdata['channel_id'] = '123'
        response = self.do_request(withdraw_postdata)
        self.assertEqual(response.status_code, ParameterException.code)
        self.assertEqual(response.json['error_code'], ParameterException.error_code)
        # self.assertEqual(response.json['message'], str({'channel_id': 'this field must be Integer type'}))

        # 测试时间格式错误
        withdraw_postdata['channel_id'] = channel_enum.value
        withdraw_postdata["maintain_begin"] = "2019/09/27 09:00:00"
        response = self.do_request(withdraw_postdata)
        self.assertEqual(response.status_code, ParameterException.code)
        self.assertEqual(response.json['error_code'], ParameterException.error_code)
        # self.assertEqual(response.json['message'], "无效的时间格式")
        withdraw_postdata["maintain_begin"] = "2019-09-27 09:00:00"

        # 测试成功添加代付通道
        ProxyChannelConfig.delete_all()
        response = self.do_request(withdraw_postdata)
        self.assertEqual(response.status_code, ResponseSuccess.code)
        self.assertEqual(response.json['error_code'], ResponseSuccess.error_code)

        channel = ProxyChannelConfig.query_latest_one(dict(channel_enum=channel_enum))
        self.assertEqual(withdraw_postdata['maintain_begin'], DateTimeKit.datetime_to_str(channel.maintain_begin))
        self.assertEqual(withdraw_postdata['channel_id'], channel.channel_enum.value)

        # 测试编辑 代付通道
        self.path = "/channel/withdraw/edit"

        withdraw_postdata['banks'] = ["4", "6", "3"]
        withdraw_postdata['limit_day_max'] = '180000'
        withdraw_postdata['maintain_begin'] = "2019-10-30 09:30:01"
        withdraw_postdata['maintain_end'] = "2019-12-30 09:30:01"
        response = self.do_request(withdraw_postdata)
        self.assertEqual(response.status_code, ResponseSuccess.code)
        self.assertEqual(response.json['error_code'], ResponseSuccess.error_code)

        channel = ProxyChannelConfig.query_latest_one(dict(channel_enum=channel_enum))
        self.assertEqual(channel_enum.value, channel.channel_enum.value)
        self.assertEqual(withdraw_postdata['maintain_begin'], DateTimeKit.datetime_to_str(channel.maintain_begin))
        self.assertEqual(withdraw_postdata['maintain_end'], DateTimeKit.datetime_to_str(channel.maintain_end))
        self.assertEqual([PaymentBankEnum(4), PaymentBankEnum(6), PaymentBankEnum(3)], channel.banks)
        self.assertEqual(180000, channel.limit_day_max)

        # 测试代付列表
        self.path = "/channel/withdraw/list"

        response = self.do_request()
        self.assertEqual(response.status_code, ResponseSuccess.code)
        self.assertEqual(response.json['error_code'], ResponseSuccess.error_code)
        self.assertEqual('1', response.json['data']['counts'])
        self.assertEqual(channel_enum.value, response.json['data']['withdraws'][0]['channel_id'])

        ProxyChannelConfig.delete_all()

    def __test_router_list(self):
        rule_dict = dict(
            merchants=[MerchantEnum.TEST.name, MerchantEnum.QF2.name, MerchantEnum.QF3.name],
            uid_list=[1, 2, 3, 4, 5],
            interface=InterfaceTypeEnum.CASHIER_H5.name,
            amount_min="5000.00",
            amount_max="50000.99",
            config_list=[
                dict(
                    payment_type=PaymentTypeEnum.WEIXIN.name,
                    priority=100,
                ),
                dict(
                    payment_type=PaymentTypeEnum.ZHIFUBAO.name,
                    priority=10,
                ),
                dict(
                    payment_type=PaymentTypeEnum.YUNSHANFU.name,
                    priority=55,
                ),
                dict(
                    payment_type=PaymentTypeEnum.BANKCARD.name,
                    priority=99,
                ),
            ]
        )

        def send_and_check_response(post_data, rsp_cls):
            rsp = self.do_request(post_data)
            self.assertEqual(rsp_cls.code, rsp.status_code)
            self.assertEqual(rsp_cls.error_code, rsp.json['error_code'], rsp.json['message'])
            return rsp

        self.path = "/channel/router/create"
        # 测试 amount_min >= amount_max
        rule_dict['amount_min'] = "1000000"
        send_and_check_response(rule_dict, DataStartMoreThanError)

        # 测试添加成功
        rule_dict['amount_min'] = "5000.33"
        send_and_check_response(rule_dict, ResponseSuccess)

        def check_item_and_data(_data, _item):
            self.assertEqual(set(_data['merchants']), set([x.name for x in _item.merchants]))
            self.assertEqual(set(_data['uid_list']), set(_item.uid_list))
            self.assertEqual(_data['interface'], _item.interface.name)
            self.assertEqual(len(_data['config_list']), len(_item.config_list))

        item = ChannelRouter.query_all()[0]
        check_item_and_data(rule_dict, item)

        # 测试修改成功
        self.path = '/channel/router/update'
        rule_dict['router_id'] = item.router_id
        rule_dict['uid_list'] = [2, 3, 8, 11111, 23981234]
        send_and_check_response(rule_dict, ResponseSuccess)
        item = ChannelRouter.query_all()[0]
        check_item_and_data(rule_dict, item)

        # 再新增一个路由
        self.path = "/channel/router/create"
        rule_dict['uid_list'] = [4, 5, 6, 7, 8]
        rule_dict['config_list'].pop(0)
        rule_dict['config_list'].pop(0)
        send_and_check_response(rule_dict, ResponseSuccess)
        item = ChannelRouter.query_all()[1]
        check_item_and_data(rule_dict, item)

        # 测试路由列表
        self.path = "/channel/router/list"
        response = send_and_check_response(rule_dict, ResponseSuccess)
        items = ChannelRouter.query_all()
        self.assertEqual(2, response.json['data']['counts'])
        self.assertEqual(items[0].router_id, response.json['data']['rules'][0]['router_id'])
        self.assertEqual(items[1].router_id, response.json['data']['rules'][1]['router_id'])

        ChannelRouter.delete_all()

    def __test_api_withdraw(self):
        """
        1. 新建用户提现订单
        :return:
        """
        order_cls = OrderWithdraw
        uid = 1000

        channel_enum = ChannelConfigEnum.CHANNEL_1001

        banks = [PaymentBankEnum(int(bank)) for bank in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]]
        proxy_channel = dict(
            fee=Decimal("2.5"),
            fee_type=PaymentFeeTypeEnum.PERCENT_PER_ORDER,
            limit_per_min=300,
            limit_per_max=1000,
            limit_day_max=0,
            trade_begin_hour=0,
            trade_begin_minute=0,
            trade_end_hour=23,
            trade_end_minute=59,
            maintain_begin=DateTimeKit.str_to_datetime("2019-12-11 09:00:00", DateTimeFormatEnum.SECONDS_FORMAT),
            maintain_end=DateTimeKit.str_to_datetime("2025-12-20 23:00:00", DateTimeFormatEnum.SECONDS_FORMAT),
            state=ChannelStateEnum.TESTING,
            banks=banks
        )
        ProxyChannelConfig.update_channel(channel_enum, **proxy_channel)

        merchant = MerchantEnum.TEST

        # 准备配置数据
        bank = BankCard.add_bank_card(
            merchant,
            uid=uid,
            bank_name="中国工商银行",
            bank_code="ICBC",
            card_no="6212260405014627955",
            account_name="张三",
            branch="广东东莞东莞市长安镇支行",
            province="广东省",
            city="东莞市",
        )

        OrderMixes.add_one_channel_config(channel_enum)
        OrderMixes.add_one_merchant_config(merchant, channel_enum, payment_way=PayTypeEnum.WITHDRAW)

        channel_config = ChannelConfig.query_latest_one(dict(channel_enum=channel_enum))

        merchant_fee_config = MerchantFeeConfig.query_latest_one(dict(
            merchant=merchant,
            payment_way=PayTypeEnum.WITHDRAW,
            payment_method=channel_enum.conf.payment_method,
        ))

        amount = Decimal("500")
        fee = BalanceKit.round_4down_5up(Decimal(merchant_fee_config.value) * amount / Decimal(100))
        # 创建提现订单
        params = dict(
            uid=uid,
            merchant=merchant,
            channel_id=channel_config.channel_id,
            mch_fee_id=merchant_fee_config.config_id,
            source=OrderSourceEnum.TESTING,
            order_type=PayTypeEnum.WITHDRAW,
            in_type=InterfaceTypeEnum.CASHIER_H5,
            amount=amount,
            bank_id=bank.id,
            fee=fee,
        )
        order, ref_id = OrderCreateCtl.create_order_event(**params)
        event = OrderEvent.query_one(dict(ref_id=ref_id), merchant=merchant, date=order.create_time)

        data = order_cls.query_by_order_id(order_id=event.order_id, merchant=merchant)

        begin_time, end_time = DateTimeKit.get_month_begin_end(year=int(DateTimeKit.get_cur_datetime().year),
                                                               month=int(DateTimeKit.get_cur_datetime().month))
        withdraw_params = dict(
            merchant_name="TEST",
            page_size=10,
            page_index=1,
            begin_time=DateTimeKit.datetime_to_str(begin_time, DateTimeFormatEnum.SECONDS_FORMAT),
            end_time=DateTimeKit.datetime_to_str(end_time, DateTimeFormatEnum.SECONDS_FORMAT),
            state="0"
        )

        self.path = "/trade_manage/withdraw/list"
        # 通过接口 查询提现订单
        response = self.do_request(json_data=withdraw_params)
        print(response.json, "&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
        self.assertEqual("1", response.json['data']['total'])
        self.assertEqual("待认领", response.json['data']['entries'][0]['state'])

        self.path = "/trade_manage/order/allowed"
        # 通过接口， 认领订单
        allowed_params = dict(
            order_id=order.id,
            merchant_name="TEST"
        )
        response = self.do_request(allowed_params)
        self.assertEqual(ResponseSuccess.code, response.status_code)
        self.assertEqual(ResponseSuccess.error_code, response.json['error_code'])
        # 查询当前订单状态是否已修改为已认领
        data = order_cls.query_by_order_id(order_id=event.order_id, merchant=merchant)
        self.assertEqual(OrderStateEnum.ALLOC, data.state)

        # 通过接口查询 审核列表 已有的认领订单为1
        self.path = '/trade_manage/withdraw/review/list'

        request_review_params = dict(
            year=str(DateTimeKit.get_cur_datetime().year),
            mouth=str(DateTimeKit.get_cur_datetime().month)
        )
        response = self.do_request(json_data=request_review_params)
        self.assertEqual(1, len(response.json['data']['entries']))
        self.assertEqual("已认领", response.json['data']['entries'][0]['state'])

        # 通过接口查询 当前可用的 代付通道
        proxy_channel_suppor = dict(
            bank_type=bank.bank_enum.name,
            merchant_name="TEST",
            amount=str(amount)
        )

        self.path = "/trade_manage/withdraw/available/channel"

        response = self.do_request(json_data=proxy_channel_suppor)
        self.assertEqual(WithdrawBankEntryResult.code, response.status_code)
        self.assertEqual(WithdrawBankEntryResult.error_code, response.json['error_code'])
        self.assertEqual(channel_enum.conf['provider'] + channel_enum.conf['mch_id'],
                         response.json['data']['entries'][0]['key'])

        # 测试人工出款 处理订单
        self.path = '/trade_manage/withdraw/person/execute'

        execute_params = dict(
            order_id=order.order_id,
            merchant="Test"
        )

        response = self.do_request(json_data=execute_params)
        self.assertEqual(ResponseSuccess.code, response.status_code)
        self.assertEqual(ResponseSuccess.error_code, response.json['error_code'])
        data = order_cls.query_by_order_id(order_id=event.order_id, merchant=merchant)
        self.assertEqual(OrderStateEnum.DEALING, data.state)

        # 测试人工出款  出款

        self.path = "/trade_manage/withdraw/person/done"
        done_params = dict(
            order_id=order.order_id,
            merchant='TEST',
            comment='测试',
            fee='5'
        )

        response = self.do_request(json_data=done_params)
        self.assertEqual(ResponseSuccess.code, response.status_code)
        self.assertEqual(ResponseSuccess.error_code, response.json['error_code'])
        data = order_cls.query_by_order_id(order_id=event.order_id, merchant=merchant)
        self.assertEqual(OrderStateEnum.SUCCESS, data.state)
