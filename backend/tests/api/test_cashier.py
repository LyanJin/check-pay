import datetime
import hashlib
from contextlib import contextmanager
from decimal import Decimal

from app.caches.auth_code import AuthCodeCache
from app.constants.auth_code import SPECIAL_SMS_AUTH_CODE
from app.enums.account import AccountTypeEnum
from app.libs.balance_kit import BalanceKit
from app.libs.error_code import ParameterException, ResponseSuccess, AccountAlreadyExitError, AuthCodeError, \
    OriPasswordError, AccountNotExistError, LoginPasswordError, TokenBadError, \
    PasswordError, RePasswordError, DisableUserError, InvalidDepositPaymentTypeError, WithdrawOrderAmountInvalidError, \
    WithdrawBankNoExistError
from app.docs.doc_cashier.auth_client import ResponseSuccessLogin
from app.libs.order_kit import OrderUtils
from app.libs.string_kit import RandomString
from app.logics.order.create_ctl import OrderCreateCtl
from app.models.balance import UserBalanceEvent, UserBalance
from app.models.bankcard import BankCard
from app.models.merchant import MerchantFeeConfig, MerchantInfo, MerchantBalanceEvent
from app.models.user import User
from config import MerchantEnum, MerchantTypeEnum, MerchantDomainConfig, DBEnum
from scripts.init_data import InitData
from tests import TestCashierBase
from app.enums.trade import PaymentBankEnum, PayTypeEnum, PayMethodEnum, OrderSourceEnum, BalanceTypeEnum, \
    BalanceAdjustTypeEnum
from app.libs.datetime_kit import DateTimeKit, DateTimeFormatEnum
from app.models.channel import ChannelConfig, ProxyChannelConfig
from app.enums.trade import PaymentFeeTypeEnum, SettleTypeEnum
from app.enums.channel import ChannelConfigEnum, ChannelStateEnum
from app.docs.doc_cashier.deposit_withdraw import ResponseDepositLimitConfig, ResponseUserBalance, ResponsePaymentType, \
    ResponseBankWithdraw, ResponseOrderEntryList


class TestCashierApi(TestCashierBase):

    @contextmanager
    def with_client(self):
        with self.app.test_client() as client:
            # 临时保存
            self.client_ctx = client
            yield
            # 用完清除
            self.client_ctx = None

    def test_cashier_api(self):
        with self.with_client():
            # 准备测试数据
            data = dict(
                # 正确的手机号码
                number='+639166660272',
                # 未注册的手机号码
                number_new='+639166660233',
                # 错误格式的手机号码
                number_invalid='9166660272',

                # 正确的验证码
                auth_code=SPECIAL_SMS_AUTH_CODE,
                # 错误的验证码
                auth_code_err='0000',
                # 验证码格式错误
                auth_code_invalid='s23d',

                # 正确的密码
                password=hashlib.md5('12Lk-M_6mn7'.encode('utf8')).hexdigest(),
                # 新密码
                password_new=hashlib.md5('abc12345'.encode('utf8')).hexdigest(),
                # 错误的密码
                password_err=hashlib.md5('002341ss'.encode('utf8')).hexdigest(),
            )

            # 执行用例
            InitData.init_merchant()
            # self.__merchant_config_check()
            self.__test_api_auth_mobile_check(data)
            self.__test_api_sms_get(data)
            self.__test_api_sms_verify(data)
            self.__test_api_register(data)
            self.__test_api_account_login(data)
            # self.__test_api_token_auth()
            self.__test_api_password_reset(data)
            self.__test_api_forget_password(data)
            self.__test_api_deposit()
            self.__test_get_order_list(PayTypeEnum.DEPOSIT)
            self.__test_api_withdraw()
            self.__test_get_order_list(PayTypeEnum.WITHDRAW)
            # 查询所有交易记录
            self.__test_get_order_list()

    def __merchant_config_check(self):
        self.path = '/health/domain/check'

        response = self.do_get_request(dict(x=1, y=2))
        self.assertEqual(ResponseSuccess.code, response.status_code)
        self.assertEqual(ResponseSuccess.error_code, response.json['error_code'])

        data = response.json['data']
        self.assertEqual(InitData.merchant.name, data['merchant'])
        self.assertEqual(set(MerchantDomainConfig.get_domains(InitData.merchant)), set(data['domains']))
        # self.assertEqual(DBEnum(InitData.merchant.name).get_db_name(), data['db'])

    @classmethod
    def __get_cache_auth_code(cls, number):
        """
        从缓存里面读出验证码再拿调用API去验证
        :param number:
        :return:
        """
        return AuthCodeCache(number).loads()

    def __test_api_forget_password(self, data):
        """
        忘记密码单元测试
        :return:
        """
        # 获取验证码
        self.path = '/auth/password/forget/get'
        response = self.do_request(dict(number=data['number_new']))
        self.assertEqual(AccountNotExistError.code, response.status_code)
        self.assertEqual(response.json['error_code'], AccountNotExistError.error_code)

        # 验证验证码
        self.path = '/auth/password/forget/verify'
        auth_code = self.__get_cache_auth_code(data['number'])
        response = self.do_request(dict(number=data['number'], auth_code=auth_code))
        self.assertEqual(ResponseSuccess.code, response.status_code)
        self.assertEqual(ResponseSuccess.error_code, response.json['error_code'], response.json['message'])

        # 密码修改成功，这次用回上上次的密码，就可以修改成功
        self.path = '/auth/password/forget/set'
        response = self.do_request(dict(number=data['number'], auth_code=auth_code, password=data['password']))
        self.assertEqual(ResponseSuccess.code, response.status_code)
        self.assertEqual(ResponseSuccess.error_code, response.json['error_code'], response.json['message'])

        # 密码修改成功后要用新密码重新登录
        self.path = '/auth/account/login'
        post_data = dict(number=data['number'], password=data['password'])
        response = self.do_request(post_data)
        self.assertEqual(response.status_code, ResponseSuccessLogin.code)
        self.assertEqual(response.json['error_code'], ResponseSuccessLogin.error_code)

        # 必须验证是否生成了token
        self.assertIsNotNone(response.json['data']['token'])

        # 新的token
        self.token = response.json['data']['token']

    def __test_api_password_reset(self, data):
        """
        测试重置密码接口
        :return: 
        """
        self.path = '/auth/password/reset'

        # 测试原始密码输入错误
        response = self.do_request(dict(ori_password=data['password_err']), path='/auth/password/reset/verify')
        self.assertEqual(response.status_code, PasswordError.code)
        self.assertEqual(response.json['error_code'], PasswordError.error_code)

        # 测试原密码连续输入错误 五次
        self.do_request(dict(ori_password=data['password_err']), path='/auth/password/reset/verify')
        self.do_request(dict(ori_password=data['password_err']), path='/auth/password/reset/verify')
        self.do_request(dict(ori_password=data['password_err']), path='/auth/password/reset/verify')
        response = self.do_request(dict(ori_password=data['password_err']), path='/auth/password/reset/verify')
        self.assertEqual(response.status_code, OriPasswordError.code)
        self.assertEqual(response.json['error_code'], OriPasswordError.error_code)
        # 通过调用 忘记密码 来更改账户状态
        forget_password_data = dict(number=data['number'], auth_code='8888', password=data['password'])
        # 通过忘记密码修改用户状态
        self.do_request(forget_password_data, path='/auth/password/forget/set')

        # 测试账户状态不可用时的返回信息
        self.do_request(dict(ori_password=data['password_err']), path='/auth/password/reset/verify')
        self.do_request(dict(ori_password=data['password_err']), path='/auth/password/reset/verify')
        self.do_request(dict(ori_password=data['password_err']), path='/auth/password/reset/verify')
        self.do_request(dict(ori_password=data['password_err']), path='/auth/password/reset/verify')
        self.do_request(dict(ori_password=data['password_err']), path='/auth/password/reset/verify')
        response = self.do_request(dict(ori_password=data['password_err']), path='/auth/password/reset/verify')
        self.assertEqual(response.status_code, DisableUserError.code)
        self.assertEqual(response.json['error_code'], DisableUserError.error_code)

        # 通过忘记密码修改用户状态
        forget_password_data = dict(number=data['number'], auth_code='8888', password=data['password'])
        self.do_request(forget_password_data, path='/auth/password/forget/set')

        # 测试原始密码输入正确
        response = self.do_request(dict(ori_password=data['password']), path='/auth/password/reset/verify')
        self.assertEqual(ResponseSuccess.code, response.status_code)
        self.assertEqual(ResponseSuccess.error_code, response.json['error_code'], response.json['message'])

        # 测试新密码与愿密码一致
        response = self.do_request(dict(ori_password=data['password'], new_password=data['password']))
        self.assertEqual(response.status_code, RePasswordError.code)
        self.assertEqual(response.json['error_code'], RePasswordError.error_code)

        # 测试成功修改密码
        response = self.do_request(dict(ori_password=data['password'], new_password=data['password_new']))
        self.assertEqual(ResponseSuccess.code, response.status_code)
        self.assertEqual(ResponseSuccess.error_code, response.json['error_code'], response.json['message'])

        # 密码修改成功后要用新密码重新登录
        self.path = '/auth/account/login'
        post_data = dict(number=data['number'], password=data['password_new'])
        response = self.do_request(post_data)
        self.assertEqual(response.status_code, ResponseSuccessLogin.code)
        self.assertEqual(response.json['error_code'], ResponseSuccessLogin.error_code)

        # 必须验证是否生成了token
        self.assertIsNotNone(response.json['data']['token'])

        # 新的token
        self.token = response.json['data']['token']

    def __test_api_token_auth(self):
        """
        测试需要token授权才能访问的API
        :return:
        """
        self.path = '/user/test'

        # 测试正确的token，返回正确的响应
        response = self.do_request()
        self.assertEqual(ResponseSuccess.code, response.status_code)
        self.assertEqual(ResponseSuccess.error_code, response.json['error_code'], response.json['message'])

        # 暂存token
        token = self.token

        # 测试无效的token
        self.token = self.token + '123'
        response = self.do_request()
        self.assertEqual(response.status_code, TokenBadError.code)
        self.assertEqual(response.json['error_code'], TokenBadError.error_code)

        # 保存token，接下来的测试用例要用到
        self.token = token

    def __test_api_account_login(self, data):
        self.path = '/auth/account/login'

        def test_auth_login_number_empty():
            """
            账户名为空
            :return:
            """
            post_data = dict(password=data['password'])
            response = self.do_request(post_data)
            self.assertEqual(ParameterException.code, response.status_code)
            self.assertEqual(ParameterException.error_code, response.json['error_code'], response.json['message'])

        def test_auth_login_password_empty():
            """
            密码为空
            :return:
            """
            post_data = dict(number=data['number'])
            response = self.do_request(post_data)
            self.assertEqual(ParameterException.code, response.status_code)
            self.assertEqual(ParameterException.error_code, response.json['error_code'], response.json['message'])

        def test_auth_login_number_no_exist():
            """
            手机号未注册
            :return:
            """
            post_data = dict(number=data['number_new'], password=data['password'])
            response = self.do_request(post_data)
            self.assertEqual(AccountNotExistError.code, response.status_code)
            self.assertEqual(AccountNotExistError.error_code, response.json['error_code'])

        def test_auth_login_password_error():
            """
            已注册用户密码错误
            :return:
            """
            post_data = dict(number=data['number'], password=data['password_err'])
            response = self.do_request(post_data)
            self.assertEqual(LoginPasswordError.code, response.status_code)
            self.assertEqual(LoginPasswordError.error_code, response.json['error_code'])

        def test_auth_login_password_five_error():
            """
            连续五次登陆密码错误则账户被封
            :return:
            """
            post_data = dict(number=data['number'], password=data['password_err'])

            self.do_request(post_data)
            self.do_request(post_data)
            self.do_request(post_data)
            response = self.do_request(post_data)

            self.assertEqual(response.status_code, OriPasswordError.code)
            self.assertEqual(response.json['error_code'], OriPasswordError.error_code)
            forget_password_data = dict(number=data['number'], auth_code='8888', password=data['password'])
            # 通过忘记密码修改用户状态
            self.do_request(forget_password_data, path='/auth/password/forget/set')

        def test_auth_login_no_continuous_five():
            """
            如果有一次登陆成功则密码输入错误次数清空
            :return:
            """
            error_password_data = dict(number=data['number'], password=data['password_err'])
            true_password_data = dict(number=data['number'], password=data['password'])

            self.do_request(error_password_data)
            self.do_request(error_password_data)
            self.do_request(error_password_data)
            self.do_request(error_password_data)

            self.do_request(true_password_data)

            self.do_request(error_password_data)
            self.do_request(error_password_data)
            self.do_request(error_password_data)
            self.do_request(error_password_data)
            response = self.do_request(error_password_data)
            self.assertEqual(response.status_code, OriPasswordError.code)
            self.assertEqual(response.json['error_code'], OriPasswordError.error_code)
            forget_password_data = dict(number=data['number'], auth_code='8888', password=data['password'])
            # 通过忘记密码修改用户状态
            self.do_request(forget_password_data, path='/auth/password/forget/set')

        def test_auth_login_continuous_six():
            """
            测试用户连续五次密码输入错误后，第六次的信息
            :return: 
            """
            error_password_data = dict(number=data['number'], password=data['password_err'])

            self.do_request(error_password_data)
            self.do_request(error_password_data)
            self.do_request(error_password_data)
            self.do_request(error_password_data)
            self.do_request(error_password_data)
            # 第六次登入时：
            response = self.do_request(error_password_data)
            self.assertEqual(response.status_code, DisableUserError.code)
            self.assertEqual(response.json['error_code'], DisableUserError.error_code)
            forget_password_data = dict(number=data['number'], auth_code='8888', password=data['password'])
            # 通过忘记密码修改用户状态
            self.do_request(forget_password_data, path='/auth/password/forget/set')

        def test_auth_login_success():
            """
            用户登陆成功
            :return:
            """
            post_data = dict(number=data['number'], password=data['password'])

            forget_password_data = dict(number=data['number'], auth_code='8888', password=data['password'])
            # 通过忘记密码修改用户状态
            response = self.do_request(forget_password_data, path='/auth/password/forget/set')

            response = self.do_request(post_data)
            self.assertEqual(ResponseSuccessLogin.code, response.status_code)
            self.assertEqual(ResponseSuccessLogin.error_code, response.json['error_code'])
            # 必须验证是否生成了token
            self.assertIsNotNone(response.json['data']['token'])
            self.assertIsNotNone(response.json['data']['service_url'])
            return response.json['data']['token']

        test_auth_login_number_empty()
        test_auth_login_password_empty()
        test_auth_login_number_no_exist()
        test_auth_login_password_error()
        test_auth_login_password_five_error()
        test_auth_login_no_continuous_five()
        test_auth_login_continuous_six()

        self.token = test_auth_login_success()

    def __test_api_register(self, data):
        # 配置API请求路径
        self.path = '/auth/account/register'

        def test_auth_register_fail_by_code():
            """
            错误的验证码
            :return:
            """
            post_data = dict(number=data['number'], auth_code=data['auth_code_err'], password=data['password'])
            response = self.do_request(post_data)
            self.assertEqual(response.status_code, AuthCodeError.code)
            self.assertEqual(response.json['error_code'], AuthCodeError.error_code)

        def test_auth_register_fail_by_number():
            """
            无效的手机号码
            :return:
            """
            post_data = dict(number=data['number_invalid'], auth_code=data['auth_code_err'], password=data['password'])
            response = self.do_request(post_data)
            self.assertEqual(ParameterException.code, response.status_code)
            self.assertEqual(ParameterException.error_code, response.json['error_code'], response.json['message'])

        def test_auth_register_success():
            """
            注册成功
            :return:
            """
            post_data = dict(number=data['number'], auth_code=data['auth_code'], password=data['password'])
            response = self.do_request(post_data)
            self.assertEqual(ResponseSuccess.code, response.status_code)
            self.assertEqual(ResponseSuccess.error_code, response.json['error_code'], response.json['message'])

        def test_auth_register_fail_by_number_repeated():
            """
            手机号码重复注册
            :return:
            """
            post_data = dict(number=data['number'], auth_code=data['auth_code'], password=data['password'])
            response = self.do_request(post_data)
            self.assertEqual(response.status_code, AccountAlreadyExitError.code)
            self.assertEqual(response.json['error_code'], AccountAlreadyExitError.error_code)

        test_auth_register_fail_by_code()
        test_auth_register_fail_by_number()
        test_auth_register_success()
        test_auth_register_fail_by_number_repeated()

    def __test_api_sms_get(self, data):
        # 配置API请求路径
        self.path = '/sms/get'

        def test_ok_86():
            response = self.do_request(dict(number='+8618912341234'))
            self.assertEqual(ResponseSuccess.code, response.status_code)
            self.assertEqual(ResponseSuccess.error_code, response.json['error_code'], response.json['message'])

        def test_ok_63():
            response = self.do_request(dict(number=data['number']))
            self.assertEqual(ResponseSuccess.code, response.status_code)
            self.assertEqual(ResponseSuccess.error_code, response.json['error_code'], response.json['message'])

        # def test_get_auth_upper_limit():
        #     self.do_request(dict(number='+8618912341234'))
        #     self.do_request(dict(number='+8618912341234'))
        #     self.do_request(dict(number='+8618912341234'))
        #     self.do_request(dict(number='+8618912341234'))
        #     response = self.do_request(dict(number='+8618912341234'))
        #     self.assertEqual(response.status_code, AuthCodeTimesLimitError.code)
        #     self.assertEqual(response.json['error_code'], AuthCodeTimesLimitError.error_code)

        def test_missing_number():
            response = self.do_request()
            self.assertEqual(ParameterException.code, response.status_code)
            self.assertEqual(ParameterException.error_code, response.json['error_code'], response.json['message'])

        # 执行用例
        # test_get_auth_upper_limit()
        test_missing_number()
        test_ok_86()
        test_ok_63()

    def __test_api_sms_verify(self, data):
        # 配置API请求路径
        self.path = '/sms/verify'

        def test_api_auth_code_long_error():
            response = self.do_request(dict(number=data['number'], auth_code='35469'))
            self.assertEqual(ParameterException.code, response.status_code)
            self.assertEqual(ParameterException.error_code, response.json['error_code'], response.json['message'])

        def test_api_auth_code_short_error():
            response = self.do_request(dict(number=data['number'], auth_code='354'))
            self.assertEqual(ParameterException.code, response.status_code)
            self.assertEqual(ParameterException.error_code, response.json['error_code'], response.json['message'])

        def test_api_auth_code_letter_error():
            response = self.do_request(dict(number=data['number'], auth_code='3n4m'))
            self.assertEqual(ParameterException.code, response.status_code)
            self.assertEqual(ParameterException.error_code, response.json['error_code'], response.json['message'])

        def test_api_auth_code_empty_error():
            response = self.do_request(dict(number=data['number'], auth_code=''))
            self.assertEqual(ParameterException.code, response.status_code)
            self.assertEqual(ParameterException.error_code, response.json['error_code'], response.json['message'])

        def test_api_auth_code_match_error():
            response = self.do_request(dict(number=data['number'], auth_code='0039'))
            self.assertEqual(response.status_code, AuthCodeError.code)
            self.assertEqual(response.json['error_code'], AuthCodeError.error_code)

        def test_api_auth_code_success():
            """
            验证码验证成功
            :return:
            """
            auth_code = self.__get_cache_auth_code(data['number'])
            response = self.do_request(dict(number=data['number'], auth_code=auth_code))
            self.assertEqual(ResponseSuccess.code, response.status_code)

        test_api_auth_code_short_error()
        test_api_auth_code_long_error()
        test_api_auth_code_letter_error()
        test_api_auth_code_empty_error()
        test_api_auth_code_match_error()
        test_api_auth_code_success()

    def __test_api_auth_mobile_check(self, data):
        # 配置API请求路径
        self.path = '/auth/mobile/check'

        def test_format_plus_error():
            """
            号码 不含 ➕
            :return:
            """
            response = self.do_request(dict(number='8613323884567'))
            self.assertEqual(ParameterException.code, response.status_code)
            self.assertEqual(ParameterException.error_code, response.json['error_code'], response.json['message'])

        def test_format_empty_error():
            """
            号码为空
            :return:
            """
            response = self.do_request(dict(number=""))
            self.assertEqual(ParameterException.code, response.status_code)
            self.assertEqual(ParameterException.error_code, response.json['error_code'], response.json['message'])

        def test_exists_error():
            """
            号码已存住
            :return:
            """
            from app.models.user import User
            account = "+639672844685"
            User.register_account(
                self.t_merchant,
                account,
                AccountTypeEnum.MOBILE,
                'abc123456789',
            )
            self.assertIsNotNone(User.query_user(self.t_merchant, account=account))
            response = self.do_request(dict(number=account))
            User.delete_account(self.t_merchant, account=account)
            self.assertEqual(response.status_code, AccountAlreadyExitError.code)
            self.assertEqual(response.json['error_code'], AccountAlreadyExitError.error_code)

        def test_format_letter_error():
            """
            号码中含有除加号外的其它字符
            :return:
            """
            response = self.do_request(dict(number="+86other_letter123"))
            self.assertEqual(ParameterException.code, response.status_code)
            self.assertEqual(ParameterException.error_code, response.json['error_code'], response.json['message'])

        def test_format_length_short_error():
            """
            号码长度过短异常
            :return:
            """
            response = self.do_request(dict(number="+8612345"))
            self.assertEqual(ParameterException.code, response.status_code)
            self.assertEqual(ParameterException.error_code, response.json['error_code'], response.json['message'])

        def test_format_length_long_error():
            """
            号码长度过长异常
            :return:
            """
            response = self.do_request(dict(number="+8612345678986123456789"))
            self.assertEqual(ParameterException.code, response.status_code)
            self.assertEqual(ParameterException.error_code, response.json['error_code'], response.json['message'])

        def test_success():
            """
            号码验证成功
            :return:
            """
            response = self.do_request(dict(number=data['number']))
            self.assertEqual(ResponseSuccess.code, response.status_code)

        test_format_empty_error()
        test_format_letter_error()
        test_exists_error()
        test_format_plus_error()
        test_format_length_long_error()
        test_format_length_short_error()
        test_success()

    def __test_api_deposit(self):
        self.path = "/auth/account/register"
        register_data = dict(
            number="+8618912341234",
            auth_code="8888",
            password="e99a18c428cb38d5f260853678922e03"
        )

        response = self.do_request(register_data)
        self.assertEqual(ResponseSuccess.code, response.status_code)
        self.assertEqual(ResponseSuccess.error_code, response.json['error_code'])

        self.path = '/auth/account/login'

        login_data = dict(
            number="+8618912341234",
            password="e99a18c428cb38d5f260853678922e03"
        )
        response = self.do_request(login_data)
        print(response.json)
        self.assertEqual(ResponseSuccessLogin.code, response.status_code)
        self.assertEqual(ResponseSuccessLogin.error_code, response.json['error_code'])
        self.token = response.json['data']['token']

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

        # print(channel1['channel_id'])
        ChannelConfig.update_channel(ChannelConfigEnum.CHANNEL_1001, **kwargs)

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

        self.path = "/deposit/limit/config/get"
        response = self.do_request()
        self.assertEqual(ResponseDepositLimitConfig.code, response.status_code)
        self.assertEqual(ResponseDepositLimitConfig.error_code, response.json['error_code'])

        self.path = "/deposit/payment/type/list"
        response = self.do_request(dict(amount=500))
        self.assertEqual(ResponsePaymentType.code, response.status_code)
        self.assertEqual(ResponsePaymentType.error_code, response.json['error_code'], response.json['message'])

        self.path = "/deposit/order/create"
        create_order_data = dict(
            payment_type="20",
            amount="400.03",
            channel_id=ChannelConfigEnum.CHANNEL_1001.value,
        )

        response = self.do_request(create_order_data)
        self.assertEqual(InvalidDepositPaymentTypeError.code, response.status_code)
        self.assertEqual(InvalidDepositPaymentTypeError.error_code, response.json['error_code'],
                         response.json['message'])

        # create_order_data['payment_type'] = '10'
        # response = self.do_request(create_order_data)
        # self.assertEqual(ResponseSuccess.code, response.status_code)
        # self.assertEqual(ResponseSuccess.error_code, response.json['error_code'])

        # create_order_data['channel_id'] = '105'
        # response = self.do_request(create_order_data)
        # self.assertEqual(InvalidDepositChannelError.code, response.status_code)
        # self.assertEqual(InvalidDepositChannelError.error_code, response.json['error_code'])

        # create_order_data['channel_id'] = '101'
        # create_order_data['payment_type'] = "20"
        # response = self.do_request(create_order_data)
        # self.assertEqual(ChannelNoValidityPeriodError.code, response.status_code)
        # self.assertEqual(ChannelNoValidityPeriodError.error_code, response.json['error_code'])

        # create_order_data['payment_type'] = "30"
        # create_order_data['channel_id'] = '107'
        # response = self.do_request(create_order_data)
        # self.assertEqual(ResponseSuccess.code, response.status_code)
        # self.assertEqual(ResponseSuccess.error_code, response.json['error_code'])

        self.path = "/user/balance/get"
        response = self.do_request()
        print(response.json)
        self.assertEqual(ResponseUserBalance.code, response.status_code)
        self.assertEqual(ResponseUserBalance.error_code, response.json['error_code'])

    def __test_api_withdraw(self):
        """
        后台准备数据：
            充值通道数据
            代付通道数据
            商户费率配置数据

        钱包端：
            1. 创建充值订单
            2. 充值
            3. 用户设置支付密码
            4. 用户绑定银行卡
            5. 获取充值配置信息(用户余额，充值最低最高限制)

        发起提现请求：

        :return:
        """
        merchant = MerchantEnum.from_name("TEST")
        info = dict(
            merchant=merchant,
            account="+8618988888888",
            auth_code="8888",
            password="e99a18c428cb38d5f260853678922e03",
            trade_pwd="b943a52cc24dcdd12bf2ba3afda92351",
            ac_type=AccountTypeEnum.MOBILE
        )
        user = User.register_account(
            info['merchant'],
            info['account'],
            info['ac_type'],
            info['password']
        )

        self.path = '/auth/account/login'

        login_data = dict(
            number=info['account'],
            password=info['password']
        )
        response = self.do_request(login_data)
        self.assertEqual(ResponseSuccessLogin.code, response.status_code)
        self.assertEqual(ResponseSuccessLogin.error_code, response.json['error_code'])
        self.token = response.json['data']['token']

        self.path = "/withdraw/banks/list"

        # 1. 向数据库添加代付通道信息
        withdraw_item = dict(
            fee="2.5",
            fee_type=PaymentFeeTypeEnum(1),
            limit_per_min="200",
            limit_per_max="5000",
            limit_day_max="50000",
            trade_begin_hour="00",
            trade_begin_minute="00",
            trade_end_hour="23",
            trade_end_minute="59",
            maintain_begin=DateTimeKit.str_to_datetime("2019-09-27 00:00:00", DateTimeFormatEnum.SECONDS_FORMAT),
            maintain_end=DateTimeKit.str_to_datetime("2019-10-20 23:59:00", DateTimeFormatEnum.SECONDS_FORMAT),
            state=ChannelStateEnum(10),
            banks=[PaymentBankEnum(1), PaymentBankEnum(2), PaymentBankEnum(4), PaymentBankEnum(3), PaymentBankEnum(15)]
        )

        ProxyChannelConfig.update_channel(ChannelConfigEnum.CHANNEL_1001, **withdraw_item)

        # 2. 向数据库插入 商户费率配置信息
        # 充值费率设置
        merchant_fee_dict = []
        merchant_fee_dict.append(dict(
            merchant=MerchantEnum.from_name('TEST'),
            payment_way=PayTypeEnum.DEPOSIT,
            value="3.5",
            fee_type=PaymentFeeTypeEnum.PERCENT_PER_ORDER,
            payment_method=PayMethodEnum.ZHIFUBAO_SAOMA,
        ))

        # 提现费率
        merchant_fee_dict.append(dict(
            merchant=MerchantEnum.from_name('TEST'),
            payment_way=PayTypeEnum.WITHDRAW,
            value="3.5",
            fee_type=PaymentFeeTypeEnum.PERCENT_PER_ORDER,
        ))

        rst, error = MerchantFeeConfig.update_fee_config(merchant, merchant_fee_dict)
        self.assertEqual(True, rst)

        # 3. 给用户和商户充值
        uid = user.uid

        ref_id = hashlib.md5('lakjdflasjfadl;kfja'.encode('utf8')).hexdigest()

        data = dict(
            uid=uid,
            merchant=merchant,
            ref_id=ref_id,
            source=OrderSourceEnum.TESTING,
            order_type=PayTypeEnum.DEPOSIT,
            bl_type=BalanceTypeEnum.AVAILABLE,
            ad_type=BalanceAdjustTypeEnum.PLUS,
            tx_id=OrderUtils.gen_normal_tx_id(uid),
            value=Decimal("10000.00"),
            comment="xxx",
        )
        rst, msg = UserBalanceEvent.update_user_balance(**data)
        self.assertEqual(0, rst)

        balance = UserBalance.query_balance(data['uid'], data['merchant']).first()

        # 添加商户余额
        data = dict(
            merchant=MerchantEnum.TEST,
            source=OrderSourceEnum.TESTING,
            order_type=PayTypeEnum.DEPOSIT,
            bl_type=BalanceTypeEnum.AVAILABLE,
            ad_type=BalanceAdjustTypeEnum.PLUS,
            tx_id=OrderUtils.gen_normal_tx_id(100),
            value=Decimal("10000.00"),
            comment=msg,
        )

        ref_id = hashlib.md5(RandomString.gen_random_str(length=128).encode('utf8')).hexdigest()
        data['ref_id'] = ref_id
        event_check = dict(total=1)
        event_check.update(data)
        rst, msg = MerchantBalanceEvent.update_balance(**data)

        self.assertEqual(0, rst)

        # 设置支付密码
        flag = User.set_payment_password(
            merchant,
            uid=uid,
            trade_pwd=info["trade_pwd"]
        )

        self.assertEqual(True, flag)

        # 绑定银行卡
        bank_info = {
            "payment_password": info['trade_pwd'],
            "bank_name": "中国工商银行",
            "bank_code": "ICBC",
            "card_no": "6212260405014627955",
            "account_name": "张三",
            "branch": "广东东莞东莞市长安镇支行",
            "province": "广东省",
            "city": "东莞市"
        }

        flag = BankCard.add_bank_card(
            merchant,
            uid=uid,
            bank_name=bank_info['bank_name'],
            bank_code=bank_info['bank_code'],
            card_no=bank_info['card_no'],
            account_name=bank_info['account_name'],
            branch=bank_info['branch'],
            province=bank_info['province'],
            city=bank_info['city']
        )
        self.assertEqual(bank_info['card_no'], flag.card_no)

        self.path = "/withdraw/limit/config/get"
        response = self.do_request()
        self.assertEqual(ResponseBankWithdraw.code, response.status_code)
        self.assertEqual(ResponseBankWithdraw.error_code, response.json['error_code'])
        self.assertEqual("10000", response.json['data']['balance'])
        self.assertEqual("200", response.json['data']['limit_min'])
        self.assertEqual("5000", response.json['data']['limit_max'])

        self.path = "/withdraw/order/create"
        create_data = dict(
            amount=1000.001,
            user_bank=1,
            trade_password=info['trade_pwd']
        )

        # 测试小于 最低限额

        create_data['amount'] = 100

        response = self.do_request(json_data=create_data)
        self.assertEqual(WithdrawOrderAmountInvalidError.code, response.status_code)
        self.assertEqual(WithdrawOrderAmountInvalidError.error_code, response.json['error_code'])

        create_data['amount'] = 6000

        response = self.do_request(json_data=create_data)
        self.assertEqual(WithdrawOrderAmountInvalidError.code, response.status_code)
        self.assertEqual(WithdrawOrderAmountInvalidError.error_code, response.json['error_code'])

        create_data['amount'] = str(500.56)
        create_data['user_bank'] = 100

        response = self.do_request(json_data=create_data)
        self.assertEqual(WithdrawBankNoExistError.code, response.status_code)
        self.assertEqual(WithdrawBankNoExistError.error_code, response.json['error_code'], response.json['message'])

        use_balance = UserBalance.query_balance(user.uid, merchant).first()
        ori_merchant = MerchantInfo.query_merchant(merchant)

        balance = ori_merchant.bl_ava - BalanceKit.round_4down_5up(
            Decimal(create_data['amount'])) * 100 - BalanceKit.round_4down_5up(
            Decimal(create_data['amount']) * Decimal(3.5))
        merchant_balance = BalanceKit.round_4down_5up(balance / Decimal(100)) * 100

        u_balance = BalanceKit.round_4down_5up(
            Decimal(use_balance.balance) / Decimal(100) - Decimal(create_data['amount'])) * Decimal(100)
        create_data['user_bank'] = 1

        response = self.do_request(json_data=create_data)
        self.assertEqual(ResponseSuccess.code, response.status_code)
        self.assertEqual(ResponseSuccess.error_code, response.json['error_code'])

        cur_balance = UserBalance.query_balance(user.uid, merchant).first()
        cur_merchant = MerchantInfo.query_merchant(merchant)

        self.assertEqual(int(merchant_balance), int(cur_merchant.bl_ava))
        self.assertEqual(int(u_balance), int(cur_balance.balance))

    def __test_get_order_list(self, payment_type=None):
        from scripts.init_data import InitData
        self.path = "/order/list"
        user = User.query_user(MerchantEnum.TEST, account=InitData.user_account)
        response = self.do_request(dict(
            uid=user.uid,
            year=2019,
            mouth=8,
            page_index=1,
            payment_type=payment_type.value if payment_type else None,
        ))
        self.assertEqual(200, response.status_code)
        self.assertEqual(ResponseOrderEntryList.error_code, response.json['error_code'])
