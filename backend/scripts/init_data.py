from decimal import Decimal

from app.enums.account import AccountTypeEnum
from app.libs.error_code import ResponseSuccess
from app.libs.order_kit import OrderUtils
from app.logics.channel.chanel_cache import ChannelLimitCacheCtl
from app.logics.channel.channel_list import ChannelListHelper
from app.logics.transaction.deposit_ctl import DepositTransactionCtl
from app.logics.transaction.withdraw_ctl import WithdrawTransactionCtl
from app.models.backoffice.admin_user import AdminUser
from app.models.balance import UserBalanceEvent, UserBalance
from app.models.bankcard import BankCard
from app.models.merchantoffice.merchant_user import MerchantUser
from app.models.order.order import OrderWithdraw
from app.models.order.order_blobal import GlobalOrderId
from app.models.user import User
from config import MerchantEnum
from app.models.merchant import MerchantFeeConfig, MerchantBalanceEvent, MerchantInfo
from app.enums.trade import BalanceTypeEnum, BalanceAdjustTypeEnum, OrderSourceEnum, SettleTypeEnum, InterfaceTypeEnum
from app.libs.datetime_kit import *
from app.models.channel import ProxyChannelConfig, ChannelConfig
from app.enums.trade import PaymentFeeTypeEnum
from app.enums.channel import ChannelConfigEnum, ChannelStateEnum
from app.enums.trade import PaymentBankEnum, PayTypeEnum, PayMethodEnum
from config import MerchantTypeEnum


class InitData:
    merchant = MerchantEnum.TEST
    user_account = "+8618912341234"
    user_account2 = "+8618900009999"
    bank_card_no = "2282283383282828288228"
    bank_card_no2 = "2282283383000000000009"
    admin_user_account = "kevin"
    password = 'e99a18c428cb38d5f260853678922e03'  # abc123
    merchant_name = 'TEST'
    merchant_id = 100
    channel_enum = ChannelConfigEnum.CHANNEL_1001
    channel_enum2 = ChannelConfigEnum.CHANNEL_1002

    @classmethod
    def init_admin_user(cls):
        if not cls.get_admin_user():
            AdminUser.register_account(account=cls.admin_user_account, login_pwd=cls.password)

    @classmethod
    def init_merchant_user(cls):
        if not cls.get_merchant_user():
            MerchantUser.register_account(mid=cls.merchant_id, account=cls.merchant_name, password=cls.password)

    @classmethod
    def get_admin_user(cls):
        return AdminUser.query_user(account=cls.admin_user_account)

    @classmethod
    def get_merchant_user(cls):
        return MerchantUser.query_user(account=cls.merchant_name)

    @classmethod
    def add_balance_to_user(cls, account, value, register=True):
        user = User.query_user(cls.merchant, account=account)
        if not user:
            if not register:
                return -10, "用户未注册"

            user = User.register_account(cls.merchant, account=account, ac_type=AccountTypeEnum.MOBILE,
                                         login_pwd=cls.password)

        data = dict(
            uid=user.uid,
            merchant=cls.merchant,
            ref_id=OrderUtils.gen_unique_ref_id(),
            source=OrderSourceEnum.MANUALLY,
            order_type=PayTypeEnum.MANUALLY,
            bl_type=BalanceTypeEnum.AVAILABLE,
            ad_type=BalanceAdjustTypeEnum.PLUS,
            tx_id=OrderUtils.gen_normal_tx_id(user.uid),
            value=Decimal(str(value)),
            comment="手动脚本修改用户可用余额",
        )
        rst, msg = UserBalanceEvent.update_user_balance(**data)
        # print(rst, msg)
        return rst, msg

    @classmethod
    def get_balance(cls, account):
        user = User.query_user(cls.merchant, account=account)
        return UserBalance.query_balance(user.uid, user.merchant).first().real_balance

    @classmethod
    def get_user_balance(cls):
        return cls.get_balance(cls.user_account)

    @classmethod
    def get_user2_balance(cls):
        return cls.get_balance(cls.user_account2)

    @classmethod
    def init_user(cls):
        user = cls.get_user()
        if not user:
            user = User.register_account(cls.merchant, account=cls.user_account, ac_type=AccountTypeEnum.MOBILE,
                                         login_pwd=cls.password)

            cls.add_balance_to_user(cls.user_account, 5000000)

        # 写入数据库
        if not cls.get_bank_card():
            bank_card = BankCard.add_bank_card(
                user.merchant,
                uid=user.uid,
                bank_name=PaymentBankEnum.ZHONGGUO.desc,
                bank_code=PaymentBankEnum.ZHONGGUO.bank_code,
                card_no=cls.bank_card_no,
                account_name="王小儿",
                branch="深圳支行",
                province="广东省",
                city="深圳市",
            )
            # print(bank_card)

    @classmethod
    def init_user2(cls):
        user = cls.get_user2()
        if not user:
            user = User.register_account(cls.merchant, account=cls.user_account2, ac_type=AccountTypeEnum.MOBILE,
                                         login_pwd=cls.password)

            data = dict(
                uid=user.uid,
                merchant=cls.merchant,
                ref_id=OrderUtils.gen_unique_ref_id(),
                source=OrderSourceEnum.MANUALLY,
                order_type=PayTypeEnum.MANUALLY,
                bl_type=BalanceTypeEnum.AVAILABLE,
                ad_type=BalanceAdjustTypeEnum.PLUS,
                tx_id=OrderUtils.gen_normal_tx_id(user.uid),
                value=Decimal("500000000"),
                comment="手动脚本修改用户可用余额",
            )
            rst, msg = UserBalanceEvent.update_user_balance(**data)
            # print(rst, msg)

        # 写入数据库
        if not cls.get_bank_card():
            bank_card = BankCard.add_bank_card(
                user.merchant,
                uid=user.uid,
                bank_name=PaymentBankEnum.ZHONGGUO.desc,
                bank_code=PaymentBankEnum.ZHONGGUO.bank_code,
                card_no=cls.bank_card_no2,
                account_name="王小儿",
                branch="深圳支行",
                province="广东省",
                city="深圳市",
            )
            # print(bank_card)

    @classmethod
    def get_user(cls):
        return User.query_user(cls.merchant, account=cls.user_account)

    @classmethod
    def get_user2(cls):
        return User.query_user(cls.merchant, account=cls.user_account2)

    @classmethod
    def get_bank_card(cls):
        return BankCard.query_bankcard_by_card_no(cls.merchant, cls.bank_card_no)

    @classmethod
    def get_bank_card2(cls):
        return BankCard.query_bankcard_by_card_no(cls.merchant, cls.bank_card_no2)

    @classmethod
    def init_merchant(cls):
        # 先创建商户
        if not cls.get_merchant_info():
            MerchantInfo.create_merchant(m_name=cls.merchant, m_type=MerchantTypeEnum.TEST)

            # 给商户加钱
            rst, msg = MerchantBalanceEvent.update_balance(
                merchant=cls.merchant,
                ref_id=OrderUtils.gen_unique_ref_id(),
                source=OrderSourceEnum.MANUALLY,
                order_type=PayTypeEnum.MANUALLY,
                bl_type=BalanceTypeEnum.AVAILABLE,
                ad_type=BalanceAdjustTypeEnum.PLUS,
                tx_id=OrderUtils.gen_normal_tx_id(10),
                value=100000000,
                comment="手动脚本修改商户可用余额"
            )
            # print(rst, msg)

        merchant_fee_list = list()
        if not cls.get_merchant_fee_config(PayTypeEnum.DEPOSIT):
            # 商户费率配置
            merchant_fee_list.append(dict(
                merchant=cls.merchant,
                payment_way=PayTypeEnum.DEPOSIT,
                value="3",
                fee_type=PaymentFeeTypeEnum.PERCENT_PER_ORDER,
                payment_method=cls.channel_enum.conf.payment_method,
            ))
            MerchantFeeConfig.update_fee_config(cls.merchant, merchant_fee_list)

            # 商户费率配置
            merchant_fee_list.append(dict(
                merchant=cls.merchant,
                payment_way=PayTypeEnum.DEPOSIT,
                value="3",
                fee_type=PaymentFeeTypeEnum.PERCENT_PER_ORDER,
                payment_method=cls.channel_enum2.conf.payment_method,
            ))
            MerchantFeeConfig.update_fee_config(cls.merchant, merchant_fee_list)

        if not cls.get_merchant_fee_config(PayTypeEnum.WITHDRAW):
            merchant_fee_list.append(dict(
                    merchant=cls.merchant,
                    payment_way=PayTypeEnum.WITHDRAW,
                    value="3.2",
                    fee_type=PaymentFeeTypeEnum.PERCENT_PER_ORDER
            ))
            MerchantFeeConfig.update_fee_config(cls.merchant, merchant_fee_list)

        merchant_config = cls.get_merchant_fee_config(PayTypeEnum.DEPOSIT)
        assert merchant_config.fee_type == PaymentFeeTypeEnum.PERCENT_PER_ORDER

        merchant_config = cls.get_merchant_fee_config(PayTypeEnum.WITHDRAW)
        assert merchant_config.fee_type == PaymentFeeTypeEnum.PERCENT_PER_ORDER

    @classmethod
    def get_merchant_info(cls):
        return MerchantInfo.query_merchant(cls.merchant)

    @classmethod
    def get_merchant_fee_config(cls, payment_way: PayTypeEnum):
        return MerchantFeeConfig.query_latest_one(query_fields=dict(
            merchant=cls.merchant,
            payment_way=payment_way,
        ))

    @classmethod
    def init_channel(cls):
        if not cls.get_deposit_channel():
            # 充值通道配置
            kwargs = dict(
                fee="2.5",
                fee_type=PaymentFeeTypeEnum.PERCENT_PER_ORDER,
                limit_per_min="100",
                limit_per_max="100000",
                trade_begin_hour="0",
                trade_begin_minute="0",
                trade_end_hour="0",
                trade_end_minute="0",
                maintain_begin=DateTimeKit.str_to_datetime("2019-09-07 09:00:00"),
                maintain_end=DateTimeKit.str_to_datetime("2019-09-07 09:00:00"),
                settlement_type=SettleTypeEnum.D0,
                state=ChannelStateEnum.TESTING if cls.merchant.is_test else ChannelStateEnum.ONLINE,
                priority="101"
            )

            ChannelConfig.update_channel(cls.channel_enum, **kwargs)
            channel_config = ChannelConfig.query_latest_one(query_fields=dict(channel_enum=cls.channel_enum))
            # print(channel_config)

            # limit_min, limit_max = ChannelLimitCacheCtl(PayTypeEnum.DEPOSIT).get_channel_limit()
            limit_min, limit_max = ChannelListHelper.get_channel_limit_range(
                merchant=cls.merchant,
                payment_way=PayTypeEnum.DEPOSIT,
            )
            # print('limit_min: %s, limit_max: %s' % (limit_min, limit_max))
            assert 0 != limit_min
            assert 0 != limit_max

        if not cls.get_withdraw_channel():
            # 提款代付通道配置
            withdraw_item = dict(
                fee="1.3",
                fee_type=PaymentFeeTypeEnum.PERCENT_PER_ORDER,
                limit_per_min="100",
                limit_per_max="100000",
                limit_day_max="50000",
                trade_begin_hour="0",
                trade_begin_minute="0",
                trade_end_hour="0",
                trade_end_minute="0",
                maintain_begin=DateTimeKit.str_to_datetime("2019-09-07 09:00:00"),
                maintain_end=DateTimeKit.str_to_datetime("2019-09-07 09:00:00"),
                state=ChannelStateEnum.TESTING if cls.merchant.is_test else ChannelStateEnum.ONLINE,
                banks=[
                    PaymentBankEnum.ZHONGGUO,
                    PaymentBankEnum.GONGSHANG,
                    PaymentBankEnum.JIANSHE,
                ]
            )
            ProxyChannelConfig.update_channel(cls.channel_enum, **withdraw_item)

            channel_config = ProxyChannelConfig.query_latest_one(query_fields=dict(channel_enum=cls.channel_enum))
            # print(channel_config)

            # limit_min, limit_max = ChannelLimitCacheCtl(PayTypeEnum.WITHDRAW).get_channel_limit()
            limit_min, limit_max = ChannelListHelper.get_channel_limit_range(
                merchant=cls.merchant,
                payment_way=PayTypeEnum.WITHDRAW,
            )
            # print('limit_min: %s, limit_max: %s' % (limit_min, limit_max))
            assert 0 != limit_min
            assert 0 != limit_max

    @classmethod
    def init_channel2(cls):
        if not cls.get_deposit_channel2():
            # 充值通道配置
            kwargs = dict(
                fee="2.5",
                fee_type=PaymentFeeTypeEnum.PERCENT_PER_ORDER,
                limit_per_min="500",
                limit_per_max="20000",
                trade_begin_hour="0",
                trade_begin_minute="0",
                trade_end_hour="0",
                trade_end_minute="0",
                maintain_begin=DateTimeKit.str_to_datetime("2019-09-07 09:00:00"),
                maintain_end=DateTimeKit.str_to_datetime("2019-09-07 09:00:00"),
                settlement_type=SettleTypeEnum.D0,
                state=ChannelStateEnum.TESTING if cls.merchant.is_test else ChannelStateEnum.ONLINE,
                priority="101"
            )

            ChannelConfig.update_channel(cls.channel_enum2, **kwargs)
            channel_config = ChannelConfig.query_latest_one(query_fields=dict(channel_enum=cls.channel_enum2))
            # print(channel_config)

            # limit_min, limit_max = ChannelLimitCacheCtl(PayTypeEnum.DEPOSIT).get_channel_limit()
            limit_min, limit_max = ChannelListHelper.get_channel_limit_range(
                merchant=cls.merchant,
                payment_way=PayTypeEnum.DEPOSIT,
            )
            # print('limit_min: %s, limit_max: %s' % (limit_min, limit_max))
            assert 0 != limit_min
            assert 0 != limit_max

        if not cls.get_withdraw_channel2():
            # 提款代付通道配置
            withdraw_item = dict(
                fee="1.3",
                fee_type=PaymentFeeTypeEnum.PERCENT_PER_ORDER,
                limit_per_min="300",
                limit_per_max="10000",
                limit_day_max="500000",
                trade_begin_hour="0",
                trade_begin_minute="0",
                trade_end_hour="0",
                trade_end_minute="0",
                maintain_begin=DateTimeKit.str_to_datetime("2019-09-07 09:00:00"),
                maintain_end=DateTimeKit.str_to_datetime("2019-09-07 09:00:00"),
                state=ChannelStateEnum.TESTING if cls.merchant.is_test else ChannelStateEnum.ONLINE,
                banks=[
                    PaymentBankEnum.ZHONGGUO,
                    PaymentBankEnum.GONGSHANG,
                    PaymentBankEnum.JIANSHE,
                ]
            )
            ProxyChannelConfig.update_channel(cls.channel_enum2, **withdraw_item)

            channel_config = ProxyChannelConfig.query_latest_one(query_fields=dict(channel_enum=cls.channel_enum2))
            # print(channel_config)

            # limit_min, limit_max = ChannelLimitCacheCtl(PayTypeEnum.WITHDRAW).get_channel_limit()
            limit_min, limit_max = ChannelListHelper.get_channel_limit_range(
                merchant=cls.merchant,
                payment_way=PayTypeEnum.WITHDRAW,
            )
            # print('limit_min: %s, limit_max: %s' % (limit_min, limit_max))
            assert 0 != limit_min
            assert 0 != limit_max

    @classmethod
    def get_deposit_channel(cls):
        return ChannelConfig.query_latest_one(query_fields=dict(channel_enum=cls.channel_enum))

    @classmethod
    def get_withdraw_channel(cls):
        return ProxyChannelConfig.query_latest_one(query_fields=dict(channel_enum=cls.channel_enum))

    @classmethod
    def get_deposit_channel2(cls):
        return ChannelConfig.query_latest_one(query_fields=dict(channel_enum=cls.channel_enum2))

    @classmethod
    def get_withdraw_channel2(cls):
        return ProxyChannelConfig.query_latest_one(query_fields=dict(channel_enum=cls.channel_enum2))

    @classmethod
    def init_sample_data(cls):
        """
        准备测试之前需要的数据
        :return:
        """
        cls.init_merchant()
        cls.init_channel()
        cls.init_channel2()
        cls.init_user()
        cls.init_user2()
        cls.init_admin_user()

    @classmethod
    def init_withdraw_order_deal(cls, amount):
        """
        初始化一个提款订单
        :param amount:
        :return:
        """
        client_ip = '127.0.0.1'
        user = cls.get_user()
        bank_card = cls.get_bank_card()
        admin_user = cls.get_admin_user()

        order, error = WithdrawTransactionCtl.order_create(
            user=user,
            amount=amount,
            client_ip=client_ip,
            user_bank_id=bank_card.card_id,
        )
        assert error is None

        rst = WithdrawTransactionCtl.order_alloc(admin_user.account, order.order_id, cls.merchant)
        assert isinstance(rst, (ResponseSuccess,))

        channel = cls.get_withdraw_channel()
        rst = WithdrawTransactionCtl.order_deal(admin_user.account, order.order_id, order.merchant,
                                                channel.channel_id, test=True)
        assert isinstance(rst, (ResponseSuccess,))

        return WithdrawTransactionCtl.get_order(order.sys_tx_id)

    @classmethod
    def init_withdraw_order_alloc(cls, amount):
        client_ip = '127.0.0.1'
        user = cls.get_user()
        bank_card = cls.get_bank_card()
        admin_user = cls.get_admin_user()

        order, error = WithdrawTransactionCtl.order_create(
            user=user,
            amount=amount,
            client_ip=client_ip,
            user_bank_id=bank_card.card_id,
        )
        assert error is None

        rst = WithdrawTransactionCtl.order_alloc(admin_user.account, order.order_id, cls.merchant)
        assert isinstance(rst, (ResponseSuccess,))

        return WithdrawTransactionCtl.get_order(order.sys_tx_id)

    @classmethod
    def get_user_latest_order(cls, uid, order_type: PayTypeEnum):
        g_order_id = GlobalOrderId.query_latest_one(uid, order_type)
        return OrderWithdraw.query_by_order_id(merchant=g_order_id.merchant, order_id=g_order_id.order_id)

    @classmethod
    def create_one_withdraw_order(cls, amount=None):
        client_ip = '127.0.0.1'
        amount = amount or Decimal("300")
        user = cls.get_user()
        bank_card = cls.get_bank_card()

        order, error = WithdrawTransactionCtl.order_create(
            user=user,
            amount=amount,
            client_ip=client_ip,
            user_bank_id=bank_card.card_id,
        )
        assert error is None

        return cls.get_user_latest_order(user.uid, PayTypeEnum.WITHDRAW)

    @classmethod
    def create_one_deposit_order(cls):

        user = InitData.get_user()
        channel_config = InitData.get_deposit_channel()

        amount = Decimal("300")

        order, error = DepositTransactionCtl.order_create(
            user=user,
            amount=amount,
            channel_enum=channel_config.channel_enum,
            source=OrderSourceEnum.TESTING,
            in_type=InterfaceTypeEnum.CASHIER_H5,
            client_ip='127.0.0.1',
        )
        assert order is not None
        assert error is None

        return DepositTransactionCtl.get_order(order.sys_tx_id)

    @classmethod
    def create_one_refund_order(cls):
        """
        创建一个失败的订单，最后退款
        :return:
        """
        amount = Decimal("300")

        order = cls.init_withdraw_order_deal(amount)
        WithdrawTransactionCtl.order_fail(order)

    @classmethod
    def create_one_transfer_order(cls):
        """
        创建一个失败的订单，最后退款
        :return:
        """
        amount = Decimal("100")
        client_ip = '127.0.0.1'

        # 判断余额是否足够
        user = cls.get_user()
        user2 = cls.get_user2()

        # 执行转账动作
        flag, msg = UserBalanceEvent.transfer(
            from_user=user,
            to_user=user2,
            merchant=cls.merchant,
            amount=amount,
            comment="转账备注"
        )
        # print(flag, msg)
