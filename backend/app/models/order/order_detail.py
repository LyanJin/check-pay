from app.enums.trade import PayTypeEnum, OrderSourceEnum, InterfaceTypeEnum, DeliverTypeEnum, CostTypeEnum
from app.extensions import db
from app.libs.balance_kit import BalanceKit
from app.libs.datetime_kit import DateTimeKit
from app.libs.ip_kit import IpKit
from app.libs.model.base import MerchantMonthColdBase
from app.libs.order_kit import OrderUtils
from app.models.order.order_blobal import GlobalOrderId
from config import MerchantEnum


class OrderDetailBase(MerchantMonthColdBase):
    __abstract__ = True

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=False, comment='订单ID')
    uid = db.Column(db.Integer, comment='用户ID', nullable=False)

    _in_type = db.Column('in_type', db.Integer, comment='接入类型', nullable=False)
    _source = db.Column('source', db.SmallInteger, comment="订单来源", nullable=False,
                        default=OrderSourceEnum.ONLINE.value)

    _amount = db.Column('amount', db.BigInteger, comment='发起金额', nullable=False)

    _tx_amount = db.Column('tx_amount', db.BigInteger, comment='实际支付金额', nullable=True)

    _offer = db.Column('offer', db.Integer, comment='优惠', nullable=True)
    _fee = db.Column('fee', db.Integer, comment='手续费', nullable=True)
    _cost = db.Column('cost', db.Integer, comment='成本', nullable=True)
    _profit = db.Column('profit', db.Integer, comment='收入', nullable=True)

    _ip = db.Column('ip', db.BigInteger, comment="ip", nullable=True)

    _done_time = db.Column('done_time', db.Integer, nullable=True, comment="完成时间")

    _merchant = db.Column('merchant', db.Integer, comment="商户ID", nullable=False)

    _cost_type = db.Column('cost_type', db.Integer, comment="手续费来源类型", nullable=True)

    comment = db.Column(db.Text, comment="备注信息", nullable=True)
    op_account = db.Column(db.String(32), comment="管理员账号", nullable=True)

    @property
    def merchant(self) -> MerchantEnum:
        return MerchantEnum(self._merchant)

    @merchant.setter
    def merchant(self, merchant: MerchantEnum):
        self._merchant = merchant.value

    @property
    def cost_type(self) -> CostTypeEnum:
        if not self._cost_type:
            return CostTypeEnum.MERCHANT
        return CostTypeEnum(self._cost_type)

    @cost_type.setter
    def cost_type(self, value: CostTypeEnum):
        self._cost_type = value.value

    @property
    def order_id(self):
        return self.id

    @order_id.setter
    def order_id(self, value):
        self.id = value

    @property
    def done_time(self):
        if self._done_time:
            return DateTimeKit.timestamp_to_datetime(self._done_time)

    @done_time.setter
    def done_time(self, value):
        self._done_time = DateTimeKit.datetime_to_timestamp(value)

    @property
    def str_done_time(self):
        if self.done_time:
            return DateTimeKit.datetime_to_str(self.done_time)
        return ''

    @property
    def in_type(self) -> InterfaceTypeEnum:
        return InterfaceTypeEnum(self._in_type)

    @in_type.setter
    def in_type(self, value: InterfaceTypeEnum):
        self._in_type = value.value

    @property
    def source(self) -> OrderSourceEnum:
        return OrderSourceEnum(self._source)

    @source.setter
    def source(self, value: OrderSourceEnum):
        self._source = value.value

    @property
    def profit(self):
        if not self._profit:
            return 0
        return BalanceKit.divide_hundred(self._profit)

    @profit.setter
    def profit(self, value):
        self._profit = BalanceKit.multiple_hundred(value)

    @property
    def cost(self):
        if not self._cost:
            return 0
        return BalanceKit.divide_hundred(self._cost)

    @cost.setter
    def cost(self, value):
        self._cost = BalanceKit.multiple_hundred(value)

    @property
    def fee(self):
        if not self._fee:
            return 0
        return BalanceKit.divide_hundred(self._fee)

    @fee.setter
    def fee(self, value):
        self._fee = BalanceKit.multiple_hundred(value)

    @property
    def offer(self):
        if not self._offer:
            return 0
        return BalanceKit.divide_hundred(self._offer)

    @offer.setter
    def offer(self, value):
        self._offer = BalanceKit.multiple_hundred(value)

    @property
    def amount(self):
        return BalanceKit.divide_hundred(self._amount)

    @amount.setter
    def amount(self, value):
        self._amount = BalanceKit.multiple_hundred(value)

    @property
    def tx_amount(self):
        if not self._tx_amount:
            return 0
        return BalanceKit.divide_hundred(self._tx_amount)

    @tx_amount.setter
    def tx_amount(self, value):
        self._tx_amount = BalanceKit.multiple_hundred(value)

    @property
    def ip(self) -> str:
        """
        整形IP转为字符串
        :return:
        """
        if not self._ip:
            return ''
        return IpKit.int_to_ip(self._ip)

    @ip.setter
    def ip(self, value: str):
        """
        存储为整数
        :param value:
        :return:
        """
        self._ip = IpKit.ip_to_int(value)

    @classmethod
    def is_base_order(cls):
        return cls.__name__ == 'OrderDetailBase'

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

        return super(OrderDetailBase, cls).query_by_create_time(begin_time, end_time, *args, **kwargs)


@MerchantMonthColdBase.init_models
class OrderDetailDeposit(OrderDetailBase):
    """
    充值订单详情
    """
    __abstract__ = True

    @property
    def order_type(self) -> PayTypeEnum:
        return PayTypeEnum.DEPOSIT


@MerchantMonthColdBase.init_models
class OrderDetailWithdraw(OrderDetailBase):
    """
    提现订单详情
    """
    __abstract__ = True

    _deliver_type = db.Column('deliver_type', db.Integer, nullable=True, comment='出款类型')
    _alloc_time = db.Column('alloc_time', db.Integer, nullable=True, comment="认领时间")
    _deal_time = db.Column('deal_time', db.Integer, nullable=True, comment="创建时间")

    @property
    def order_type(self) -> PayTypeEnum:
        return PayTypeEnum.WITHDRAW

    @property
    def deliver_type(self) -> DeliverTypeEnum:
        if self._deliver_type:
            return DeliverTypeEnum(self._deliver_type)

    @deliver_type.setter
    def deliver_type(self, value: DeliverTypeEnum):
        self._deliver_type = value.value

    @property
    def alloc_time(self):
        if self._alloc_time:
            return DateTimeKit.timestamp_to_datetime(self._alloc_time)

    @alloc_time.setter
    def alloc_time(self, value):
        self._alloc_time = DateTimeKit.datetime_to_timestamp(value)

    @property
    def str_alloc_time(self):
        if self.alloc_time:
            return DateTimeKit.datetime_to_str(self.alloc_time)
        return ''

    @property
    def deal_time(self):
        if self._deal_time:
            return DateTimeKit.timestamp_to_datetime(self._deal_time)

    @deal_time.setter
    def deal_time(self, value):
        self._deal_time = DateTimeKit.datetime_to_timestamp(value)

    @property
    def str_deal_time(self):
        if self.deal_time:
            return DateTimeKit.datetime_to_str(self.deal_time)
        return ''
