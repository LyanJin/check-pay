import json

from app.enums.trade import OrderStateEnum, PayTypeEnum, OrderSourceEnum, SettleStateEnum, DeliverStateEnum, \
    PayMethodEnum
from app.extensions import db
from app.libs.balance_kit import BalanceKit
from app.libs.datetime_kit import DateTimeKit
from app.libs.model.base import MerchantMonthColdBase
from app.libs.order_kit import OrderUtils
from app.models.order.order_blobal import GlobalOrderId
from config import MerchantEnum


class OrderBase(MerchantMonthColdBase):
    """
    订单基本信息表
    优先使用id/sys_tx_id/mch_tx_id查询，是唯一索引
    用户侧，使用uid和create_time查询，联合索引
    """
    __abstract__ = True

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=False, comment='订单ID')
    _update_time = db.Column('update_time', db.Integer, nullable=False, comment="更新时间")
    uid = db.Column(db.Integer, comment='用户ID', nullable=False)

    sys_tx_id = db.Column(db.String(128), comment="系统交易ID", nullable=False)
    mch_tx_id = db.Column(db.String(128), comment="商户交易ID", nullable=False)
    channel_tx_id = db.Column(db.String(128), comment="通道交易ID", nullable=True)

    _amount = db.Column('amount', db.BigInteger, comment='订单发起金额', nullable=False)
    _tx_amount = db.Column('tx_amount', db.BigInteger, comment='实际支付金额', nullable=True)

    _source = db.Column('source', db.SmallInteger, comment="订单来源", nullable=False,
                        default=OrderSourceEnum.ONLINE.value)
    _p_method = db.Column('p_method', db.SmallInteger, comment="支付方法", nullable=True)

    _state = db.Column('state', db.SmallInteger, comment="订单状态", nullable=False, default=OrderStateEnum.INIT.value)
    _settle = db.Column('settle', db.SmallInteger, comment="结算状态", nullable=False, default=SettleStateEnum.INIT.value)
    _deliver = db.Column('deliver', db.SmallInteger, comment="发货(通知)状态", nullable=False,
                         default=DeliverStateEnum.INIT.value)

    # ABSChannelConfig 表中的主键ID，提款发起时不填，可以为空
    channel_id = db.Column(db.Integer, comment='渠道费率配置ID', nullable=True)
    # MerchantFeeConfig 表的主键ID，提款发起时不填，可以为空
    mch_fee_id = db.Column(db.Integer, comment='商户费率配置ID', nullable=True)

    notify_url = db.Column(db.String(256), comment="通知URL", nullable=True)
    extra = db.Column(db.Text, comment="透传数据", nullable=True)

    _merchant = db.Column('merchant', db.Integer, comment="商户ID", nullable=False)

    UNION_INDEX = [
        ('uid', 'create_time'),
        ('merchant', 'create_time'),
        ('state', 'create_time'),
    ]
    UNION_UNIQUE_INDEX = [
        ('merchant', 'sys_tx_id'),
        ('merchant', 'mch_tx_id'),
    ]

    @property
    def merchant(self) -> MerchantEnum:
        return MerchantEnum(self._merchant)

    @merchant.setter
    def merchant(self, merchant: MerchantEnum):
        self._merchant = merchant.value

    @property
    def order_id(self):
        return self.id

    @order_id.setter
    def order_id(self, value):
        self.id = value

    @property
    def pay_method(self) -> PayMethodEnum:
        if self._p_method:
            return PayMethodEnum(self._p_method)

    @pay_method.setter
    def pay_method(self, value: PayMethodEnum):
        if value:
            self._p_method = value.value

    @property
    def source(self) -> OrderSourceEnum:
        return OrderSourceEnum(self._source)

    @source.setter
    def source(self, value: OrderSourceEnum):
        self._source = value.value

    @property
    def update_time(self):
        return DateTimeKit.timestamp_to_datetime(self._update_time)

    @update_time.setter
    def update_time(self, value):
        self._update_time = DateTimeKit.datetime_to_timestamp(value)

    @property
    def str_update_time(self):
        return DateTimeKit.datetime_to_str(self.update_time)

    @property
    def amount(self):
        return BalanceKit.divide_hundred(self._amount)

    @amount.setter
    def amount(self, value):
        self._amount = BalanceKit.multiple_hundred(value)

    @property
    def settle(self) -> SettleStateEnum:
        return SettleStateEnum(self._settle)

    @settle.setter
    def settle(self, value: SettleStateEnum):
        self._settle = value.value

    @property
    def deliver(self) -> DeliverStateEnum:
        return DeliverStateEnum(self._deliver)

    @deliver.setter
    def deliver(self, value: DeliverStateEnum):
        self._deliver = value.value

    @property
    def tx_amount(self):
        if not self._tx_amount:
            return 0
        return BalanceKit.divide_hundred(self._tx_amount)

    @tx_amount.setter
    def tx_amount(self, value):
        self._tx_amount = BalanceKit.multiple_hundred(value)

    @property
    def state(self) -> OrderStateEnum:
        return OrderStateEnum(self._state)

    @state.setter
    def state(self, value: OrderStateEnum):
        self._state = value.value

    @classmethod
    def is_base_order(cls):
        return cls.__name__ == 'OrderBase'

    @classmethod
    def query_by_order_id(cls, merchant, order_id, create_time=None):
        """
        更具订单号查询订单
        :param merchant:
        :param order_id:
        :param create_time:
        :return:
        """
        if cls.is_base_order():
            raise RuntimeError('can not query by base order')

        if not create_time:
            g_order_id = GlobalOrderId.query_global_id(order_id)
            if not g_order_id:
                return None
            create_time = g_order_id.create_time

        return cls.query_one(dict(id=order_id), date=create_time)

    @classmethod
    def query_by_tx_id(cls, tx_id):
        """
        根据交易ID查询订单
        :param tx_id:
        :return:
        """
        if cls.is_base_order():
            raise RuntimeError('can not query by base order')

        order_id = OrderUtils.parse_tx_id(tx_id)
        g_order_id = GlobalOrderId.query_global_id(order_id)
        if not g_order_id:
            return None

        return cls.query_by_order_id(g_order_id.merchant, order_id, g_order_id.create_time)

    @classmethod
    def query_by_uid_someday(cls, merchant, uid, someday, **kwargs):
        """
        查询用户这某天的订单
        uid和create_time有联合索引，查询速度应该比较快
        :param merchant:
        :param uid:
        :param someday:
        :return:
        """
        if cls.is_base_order():
            raise RuntimeError('can not query by base order')

        begin_time, end_time = DateTimeKit.get_day_begin_end(someday)
        return cls.query_by_create_time(begin_time, end_time, date=someday, merchant=merchant, **kwargs).filter_by(
            uid=uid)

    @classmethod
    def query_by_create_time(cls, begin_time, end_time, *args, **kwargs):
        if cls.is_base_order():
            raise RuntimeError('can not query by base order')

        return super(OrderBase, cls).query_by_create_time(begin_time, end_time, *args, **kwargs)


@MerchantMonthColdBase.init_models
class OrderDeposit(OrderBase):
    """
    充值订单
    """
    __abstract__ = True

    result_url = db.Column(db.String(256), comment="重定向URL", nullable=True)

    @property
    def order_type(self) -> PayTypeEnum:
        return PayTypeEnum.DEPOSIT

    @property
    def repr_amount(self):
        # 充值是正数
        return self.amount


@MerchantMonthColdBase.init_models
class OrderWithdraw(OrderBase):
    """
    提现订单
    """
    __abstract__ = True

    # BankCard 的主键ID
    bank_id = db.Column(db.Integer, comment='用户银行卡ID', nullable=True)
    # 银行卡信息
    _bank_info = db.Column('bank_info', db.Text, comment="银行卡信息", nullable=True)

    @property
    def order_type(self) -> PayTypeEnum:
        return PayTypeEnum.WITHDRAW

    @property
    def repr_amount(self):
        # 提现是负数的展示
        return -self.amount

    @property
    def bank_info(self):
        if not self._bank_info:
            return dict()

        return json.loads(self._bank_info)

    @bank_info.setter
    def bank_info(self, value: dict):
        if not value:
            return

        self._bank_info = json.dumps(value)

    def get_bank_card(self, valid_check=True):
        """
        获取这个订单绑定的银行卡信息
        :return:
        """
        from app.models.bankcard import BankCard

        if self.bank_id:
            return BankCard.query_bankcard_by_id(self.bank_id, valid_check=valid_check)

        if self.bank_info:
            return BankCard.generate_model(**self.bank_info)
