import copy
import datetime
import json
import traceback
from operator import attrgetter
from typing import List

from flask import current_app
from sqlalchemy.exc import IntegrityError

from app.caches.channel_limit import ChannelDayLimitCache
from app.enums.channel import ChannelStateEnum, ChannelConfigEnum, ChannelReasonEnum
from app.enums.trade import SettleTypeEnum, PaymentFeeTypeEnum, PaymentBankEnum, InterfaceTypeEnum, \
    PayMethodEnum, PaymentTypeEnum
from app.extensions import db
from app.libs.balance_kit import BalanceKit
from app.libs.datetime_kit import DateTimeKit
from app.libs.error_code import SqlIntegrityError, ChannelSqlIntegrityError
from app.libs.geo_ip.geo_ip import GeoIpKit
from app.libs.model.base import ModelBase
from app.libs.model.mix import AdminLogMix
from app.libs.string_kit import StringParser
from app.models.backoffice.admin_log import AdminLog
from config import MerchantEnum


class ABSChannelConfig(AdminLogMix, ModelBase):
    """
    通道配置抽象类
    """
    __abstract__ = True
    admin_log_model = AdminLog

    valid = db.Column(db.SmallInteger, comment='是否删除', nullable=True, default=ModelBase.VALID)

    _channel = db.Column('channel', db.Integer, nullable=False, comment='渠道配置')

    version = db.Column(db.Integer, comment="版本", nullable=False, default=1)

    _fee = db.Column('fee', db.Integer, comment="成本费率", nullable=False, default=0)

    _fee_type = db.Column('fee_type', db.SmallInteger, comment="费用类型", nullable=False,
                          default=PaymentFeeTypeEnum.PERCENT_PER_ORDER.value)

    _state = db.Column('state', db.SmallInteger, comment="状态", nullable=False, default=ChannelStateEnum.TESTING.value)

    _limit_per_min = db.Column('per_min', db.Integer, comment="单笔交易限额下限", nullable=False, default=0)
    _limit_per_max = db.Column('per_max', db.Integer, comment="单笔交易限额上限", nullable=False, default=0)

    _limit_day_max = db.Column('day_max', db.Integer, comment="日交易限额上限", nullable=False, default=0)

    trade_begin_hour = db.Column('hour_begin', db.SmallInteger, comment="开始交易时间(时)", nullable=False, default=0)
    trade_begin_minute = db.Column('minute_begin', db.SmallInteger, comment="开始交易时间(分)", nullable=False, default=0)

    trade_end_hour = db.Column('hour_end', db.SmallInteger, comment="结束交易时间(时)", nullable=False, default=0)
    trade_end_minute = db.Column('minute_end', db.SmallInteger, comment="结束交易时间(分)", nullable=False, default=0)

    _maintain_begin = db.Column('main_begin', db.Integer, comment="开始维护时间", nullable=False, default=0)
    _maintain_end = db.Column('main_end', db.Integer, comment="结束维护时间", nullable=False, default=0)

    @property
    def channel_id(self):
        return self.id

    @property
    def short_description(self):
        return ('{desc}: {fee}{fee_type}, 上线状态：{state}, 健康状态：{reason}，金流累计: {daily_amount}, '
                '每天限额：{daily_limit}，版本: {version}').format(
            version=self.version,
            fee=self.fee,
            fee_type=self.fee_type.desc,
            state=self.state.desc,
            desc=self.channel_enum.desc,
            reason=self.get_reason_desc(False),
            daily_amount=self.daily_amount,
            daily_limit=self.limit_day_max,
        )

    @property
    def channel_enum(self) -> ChannelConfigEnum:
        return ChannelConfigEnum(self._channel)

    @channel_enum.setter
    def channel_enum(self, value: ChannelConfigEnum):
        self._channel = value.value

    @property
    def fee(self):
        return BalanceKit.divide_hundred(self._fee)

    @fee.setter
    def fee(self, value):
        self._fee = BalanceKit.multiple_hundred(value)

    @property
    def fee_type(self) -> PaymentFeeTypeEnum:
        return PaymentFeeTypeEnum(self._fee_type)

    @fee_type.setter
    def fee_type(self, value: PaymentFeeTypeEnum):
        self._fee_type = value.value

    @property
    def state(self) -> ChannelStateEnum:
        return ChannelStateEnum(self._state)

    @state.setter
    def state(self, value: ChannelStateEnum):
        self._state = value.value

    @property
    def is_testing(self):
        return self.state == ChannelStateEnum.TESTING

    @property
    def limit_per_min(self):
        return BalanceKit.divide_hundred(self._limit_per_min)

    @limit_per_min.setter
    def limit_per_min(self, value):
        self._limit_per_min = BalanceKit.multiple_hundred(value)

    @property
    def limit_per_max(self):
        return BalanceKit.divide_hundred(self._limit_per_max)

    @limit_per_max.setter
    def limit_per_max(self, value):
        self._limit_per_max = BalanceKit.multiple_hundred(value)

    @property
    def limit_day_max(self):
        if not self._limit_day_max:
            return 0
        return BalanceKit.divide_hundred(self._limit_day_max)

    @limit_day_max.setter
    def limit_day_max(self, value):
        if value != 0:
            self._limit_day_max = BalanceKit.multiple_hundred(value)
        else:
            self._limit_day_max = 0

    @property
    def maintain_begin(self):
        if self._maintain_begin == 0:
            return ""
        return DateTimeKit.timestamp_to_datetime(self._maintain_begin)

    @maintain_begin.setter
    def maintain_begin(self, value):
        if value:
            self._maintain_begin = DateTimeKit.datetime_to_timestamp(value)
        else:
            self._maintain_begin = 0

    @property
    def maintain_end(self):
        if self._maintain_end == 0:
            return ""
        return DateTimeKit.timestamp_to_datetime(self._maintain_end)

    @maintain_end.setter
    def maintain_end(self, value):
        if value:
            self._maintain_end = DateTimeKit.datetime_to_timestamp(value)
        else:
            self._maintain_end = 0

    @property
    def begin_trade_time(self):
        return DateTimeKit.from_hour_minute(self.trade_begin_hour, self.trade_begin_minute)

    @property
    def end_trade_time(self):
        return DateTimeKit.from_hour_minute(self.trade_end_hour, self.trade_end_minute)

    @property
    def daily_amount(self):
        """
        每天金流累计
        :return:
        """
        return ChannelDayLimitCache().get_day_amount(self.channel_enum)

    def is_in_trade_time(self, end_delta: datetime.timedelta = datetime.timedelta(minutes=5)):
        """
        判断当前通道是否处于交易时间内
        :param end_delta:
        :return:
        """
        if (self.trade_begin_hour == 0 and self.trade_begin_minute == 0) and (
                (self.trade_end_hour == 0 and self.trade_end_minute == 0)
                or
                (self.trade_end_hour == 23 and self.trade_end_minute == 59)
        ):
            # 未设置交易时间，或者结束时间为23点59
            return True

        begin_time = self.begin_trade_time
        end_time = self.end_trade_time

        if end_delta:
            end_time -= end_delta

        cur_datetime = DateTimeKit.get_cur_datetime()

        if end_time < begin_time:
            # 如果设置的结束时间小于开始时间，比如交易周期是早上9点到凌晨的2点，那么交易时间是9点到0点以及0点到2点
            return cur_datetime <= end_time or cur_datetime >= begin_time

        return begin_time <= cur_datetime <= end_time

    def is_in_maintain_time(self, end_delta: datetime.timedelta = datetime.timedelta(minutes=5)):
        """
        判断当前通道是否处于维护时间内
        :param end_delta:
        :return:
        """
        begin_time = self.maintain_begin
        end_time = self.maintain_end

        if not begin_time or not end_time:
            # 未设置维护时间
            return False

        if end_delta:
            end_time -= end_delta

        return begin_time <= DateTimeKit.get_cur_datetime() <= end_time

    def is_amount_per_limit(self, amount):
        """
        判断金额是否达到单笔金额上下限
        :param amount:
        :return:
        """
        if self.limit_per_max and amount > self.limit_per_max:
            return True

        if self.limit_per_min and amount < self.limit_per_min:
            return True

        return False

    def is_amount_day_limit(self, amount=0):
        """
        判断金额是否达到当天累加金额
        :param amount:
        :return:
        """
        if not self.limit_day_max:
            # 没有限制
            return False

        daily_amount = self.daily_amount
        return daily_amount + amount >= self.limit_day_max

    def is_ip_forbidden(self, client_ip):
        """
        判断IP是否可以使用这条通道
        :param client_ip:
        :return:
        """
        if self.channel_enum.is_china_ip_required():
            return not GeoIpKit(client_ip).is_ip_from_china()
        return False

    def is_channel_valid(self, test=False, amount=0, client_ip=None):
        """
        判断一条通道是否有效
        :param test: 是否包含测试状态的通道
        :param amount: 金额
        :param client_ip: 用户ip
        :return:
        """
        if not self.state.is_available(test):
            return False

        if self.is_in_maintain_time():
            return False

        if not self.is_in_trade_time():
            return False

        if amount:
            if self.is_amount_per_limit(amount):
                return False

        if self.is_amount_day_limit(amount):
            return False

        if client_ip:
            if self.is_ip_forbidden(client_ip):
                return False

        return True

    def get_reason_desc(self, test=False):
        """
        获取通道不可用的原因
        :param test:
        :return:
        """
        if not self.state.is_available(test):
            return self.state.desc

        if self.is_in_maintain_time():
            return ChannelReasonEnum.MAINTAIN.desc

        if not self.is_in_trade_time():
            return ChannelReasonEnum.TRADE_TIME_LIMIT.desc

        if self.is_amount_day_limit():
            return ChannelReasonEnum.DAY_LIMIT.desc

        return '正常'

    @classmethod
    def query_latest_one(cls, query_fields):
        """
        以version倒序,查询最新的一个配置
        :param query_fields:
        :return:
        """
        params = dict()

        if 'channel_enum' in query_fields:
            # 根据通道配置来查询，先转换一下类型
            params['_channel'] = query_fields['channel_enum'].value

        return cls.query_one_order_by(query_fields=params, order_fields=[cls.version.desc()])

    @classmethod
    def query_by_channel_id(cls, channel_id: int):
        """
        根据主键查询唯一一条配置
        :param channel_id:
        :return:
        """
        return cls.query_by_id(channel_id)

    @classmethod
    def update_channel(cls, channel_enum: ChannelConfigEnum, **kwargs):
        """
        更新通道，也就是增加一个新版本的通道
        :param channel_enum:
        :param kwargs:
        :return:
        """
        kwargs['channel_enum'] = channel_enum

        models = list()

        kwargs['version'] = 1

        model = cls.query_latest_one(query_fields=dict(channel_enum=channel_enum))
        if model:
            kwargs['version'] += model.version

        rst = cls.add_model(fields=kwargs)
        models.append(rst['model'])

        log_model = cls.add_admin_log(rst['model'])
        log_model and models.append(log_model)

        try:
            cls.commit_models(models=models)
        except IntegrityError as e:
            current_app.logger.error(str(e), exc_info=True)
            return False, ChannelSqlIntegrityError()

        return True, None

    @classmethod
    def filter_latest_items(cls, items, ret_dict=False):
        """
        过滤出最新的配置，同一个渠道下的旧的配置会被排除掉
        :param items:
        :param ret_dict:
        :return:
        """
        # 按version值倒序，version值越大，记录越新
        items = sorted(items, key=attrgetter('version'), reverse=True)

        latest = dict()
        key = list()
        for item in items:
            if item.channel_enum.value in latest:
                # 已经存在的配置直接跳过
                continue
            latest[item.channel_enum.value] = item
            if item.valid is ModelBase.INVALID:
                key.append(item.channel_enum.value)

        for keys in key:
            latest.pop(keys)

        if ret_dict:
            return latest
        return latest.values()

    @classmethod
    def get_latest_active_configs(cls, ret_dict=False):
        """
        获取最新的有效的配置
        :param ret_dict:
        :return:
        """
        channel_configs = cls.query_all()
        return cls.filter_latest_items(channel_configs, ret_dict)


class ChannelConfig(ABSChannelConfig):
    """
    通道配置
    """
    _settlement_type = db.Column('st_type', db.Integer, comment="结算方式", nullable=False, default=0)
    priority = db.Column(db.Integer, comment="优先级(用于路由)", nullable=False, default=0)

    __table_args__ = (
        # 联合唯一索引
        db.UniqueConstraint('channel', 'version', name='uix_channel_config_channel_version'),
    )

    @property
    def settlement_type(self) -> SettleTypeEnum:
        return SettleTypeEnum(self._settlement_type)

    @settlement_type.setter
    def settlement_type(self, value: SettleTypeEnum):
        self._settlement_type = value.value


class ProxyChannelConfig(ABSChannelConfig):
    """
    代付通道配置
    """
    _banks = db.Column('banks', db.String(length=128), comment="支持的银行", nullable=False, default="")

    __table_args__ = (
        # 联合唯一索引
        db.UniqueConstraint('channel', 'version', name='uix_proxy_channel_config_channel_version'),
    )

    @property
    def banks(self):
        bank_list = list()
        for value in StringParser(to_type=int).split(self._banks):
            bank_list.append(PaymentBankEnum(value))
        return bank_list

    @banks.setter
    def banks(self, bank_list: List[PaymentBankEnum]):
        self._banks = StringParser().join([x.value for x in bank_list])


class RouterBase(AdminLogMix, ModelBase):
    __abstract__ = True
    admin_log_model = AdminLog

    _interface = db.Column('interface', db.SmallInteger, comment="接入类型", nullable=True)
    _amount_min = db.Column('amount_min', db.Integer, comment="交易金额下限", nullable=True)
    _amount_max = db.Column('amount_max', db.Integer, comment="交易金额上限", nullable=True)
    _merchants = db.Column('merchants', db.Text, comment="商户列表", nullable=True)
    _uid_list = db.Column('uid_list', db.Text, comment="用户列表", nullable=True)

    @classmethod
    def get_one_match_router(cls, routers, interface=None, amount=0, merchant=None, uid=None):
        params = copy.deepcopy(locals())
        params.pop('cls')
        params.pop('routers')

        for router in routers:
            if not router.has_condition():
                continue

            if router.is_router_match(**params):
                return router

        return None

    @classmethod
    def get_no_condition_routers(cls, routers):
        """
        获得一个没有配置任何条件的路由
        :param routers:
        :return:
        """
        return [x for x in routers if not x.has_condition()]

    def has_condition(self):
        """
        是否有配置匹配规则
        :return:
        """
        return self.get_conditions_length() > 0

    def get_conditions_length(self):
        params = [self.amount_max and self.amount_min, self.interface, self.merchants, self.uid_list]
        return self.calc_true_item_length(params)

    @classmethod
    def calc_true_item_length(cls, params: list):
        """
        获取为真值的元素个数
        :param params:
        :return:
        """
        return len([x for x in params if x])

    def is_router_match(self, interface=None, amount=0, merchant=None, uid=None):
        """
        判断输入条件是否匹配规则，需要已经配置的条件全部都匹配
        :param interface:
        :param amount:
        :param merchant:
        :param uid:
        :return:
        """
        params = copy.deepcopy(locals())
        params.pop('self')

        match_count = 0
        if interface and self.interface == interface:
            match_count += 1
        if amount and self.amount_min <= amount <= self.amount_max:
            match_count += 1
        if merchant and merchant in self.merchants:
            match_count += 1
        if uid and uid in self.uid_list:
            match_count += 1

        return match_count == self.get_conditions_length()

    @property
    def router_id(self):
        return self.id

    @property
    def merchants(self):
        if not self._merchants:
            return []
        _values = StringParser(',', int).split(self._merchants)
        return [MerchantEnum(v) for v in _values]

    @classmethod
    def dumps_merchants(cls, merchant_list: List[MerchantEnum]):
        return StringParser(',', int).join([v.value for v in merchant_list])

    @property
    def list_merchants(self):
        return [m.name for m in self.merchants]

    @property
    def uid_list(self):
        if not self._uid_list:
            return []
        return StringParser(',', int).split(self._uid_list)

    @classmethod
    def dumps_uid_list(cls, uid_list):
        return StringParser(',', int).join(uid_list or [])

    @property
    def interface(self) -> InterfaceTypeEnum:
        if self._interface:
            return InterfaceTypeEnum(self._interface)

    @interface.setter
    def interface(self, value: InterfaceTypeEnum):
        if value:
            self._interface = value.value
        else:
            self._interface = None

    @property
    def amount_min(self):
        if self._amount_min:
            return BalanceKit.divide_hundred(self._amount_min)
        return 0

    @amount_min.setter
    def amount_min(self, value):
        if value:
            self._amount_min = BalanceKit.multiple_hundred(value)
        else:
            self._amount_min = 0

    @property
    def amount_max(self):
        if self._amount_max:
            return BalanceKit.divide_hundred(self._amount_max)
        return 0

    @amount_max.setter
    def amount_max(self, value):
        if value:
            self._amount_max = BalanceKit.multiple_hundred(value)
        else:
            self._amount_max = 0

    @classmethod
    def _create_rule(cls, extra_fields: dict, amount_min=None, amount_max=None, interface: InterfaceTypeEnum = None,
                     merchants=None, uid_list=None):
        """
        创建引导规则
        :param extra_fields:
        :param amount_min:
        :param amount_max:
        :param interface:
        :param merchants:
        :param uid_list:
        :return:
        """
        models = list()

        fields = dict(
            amount_min=amount_min,
            amount_max=amount_max,
            interface=interface,
            _merchants=cls.dumps_merchants(merchants),
            _uid_list=cls.dumps_uid_list(uid_list),
        )
        fields.update(extra_fields)
        rst = cls.add_model(fields=fields)
        model = rst['model']
        models.append(model)

        log_model = cls.add_admin_log(model)
        log_model and models.append(log_model)

        cls.commit_models(models=models)

        return model

    @classmethod
    def _update_rule(cls, router_id, extra_fields: dict, amount_min=None, amount_max=None,
                     interface: InterfaceTypeEnum = None,
                     merchants=None, uid_list=None):
        """
        更新引导规则
        :param router_id:
        :param extra_fields:
        :param amount_min:
        :param amount_max:
        :param interface:
        :param merchants:
        :param uid_list:
        :return:
        """
        models = list()

        fields = dict(
            amount_min=amount_min,
            amount_max=amount_max,
            interface=interface,
            _merchants=cls.dumps_merchants(merchants),
            _uid_list=cls.dumps_uid_list(uid_list),
        )

        fields.update(extra_fields)

        rst = cls.update_model(fields=fields, query_fields=dict(id=router_id))

        if rst['code'] != 0:
            current_app.logger.error(rst['msg'])
            return None, rst['msg']

        model = rst['model']
        models.append(model)

        log_model = cls.add_admin_log(model)
        log_model and models.append(log_model)

        cls.commit_models(models=models)

        return model, None


class ChannelRouter(RouterBase):
    """
    钱包测支付类型引导，控制钱包端支付类型的排序和适用条件
    """
    _config_list = db.Column('config_list', db.Text, comment="支付类型配置", nullable=False)

    @property
    def config_list(self):
        _list = list()
        value = json.loads(self._config_list)
        for x in value:
            x['payment_type'] = PaymentTypeEnum.from_name(x['payment_type'])
            _list.append(x)
        return _list

    @classmethod
    def dumps_config_list(cls, config_list, to_json=True):
        _list = copy.deepcopy(config_list)
        for x in _list:
            x['payment_type'] = x['payment_type'].name

        if to_json:
            return json.dumps(_list, separators=[',', ':'])
        else:
            return _list

    @property
    def dict_config_list(self):
        return self.dumps_config_list(self.config_list, to_json=False)

    @classmethod
    def create_rule(cls, config_list, amount_min=None, amount_max=None, interface: InterfaceTypeEnum = None,
                    merchants=None, uid_list=None):
        """
        创建引导规则
        """
        params = copy.deepcopy(locals())
        params.pop('cls')
        params.pop('config_list')

        fields = dict(
            _config_list=cls.dumps_config_list(config_list),
        )
        return cls._create_rule(extra_fields=fields, **params)

    @classmethod
    def update_rule(cls, router_id, config_list, amount_min=None, amount_max=None, interface: InterfaceTypeEnum = None,
                    merchants=None, uid_list=None):
        """
        更新引导规则
        """
        params = copy.deepcopy(locals())
        params.pop('cls')
        params.pop('config_list')

        fields = dict(
            _config_list=cls.dumps_config_list(config_list),
        )
        return cls._update_rule(extra_fields=fields, **params)


class ChannelRouter2(RouterBase):
    """
    通道路由，控制通道适用的条件
    """
    _channel = db.Column('channel', db.Integer, comment="通道类型", nullable=False, unique=True)

    @property
    def channel_enum(self) -> ChannelConfigEnum:
        return ChannelConfigEnum(self._channel)

    @channel_enum.setter
    def channel_enum(self, value: ChannelConfigEnum):
        self._channel = value.value

    @classmethod
    def update_router(cls, channel_enum, amount_min=None, amount_max=None,
                      interface: InterfaceTypeEnum = None,
                      merchants=None, uid_list=None):
        """
        更新引导规则
        :return:
        """
        params = copy.deepcopy(locals())
        params.pop('cls')
        params.pop('channel_enum')

        fields = dict(
            channel_enum=channel_enum,
        )
        query_fields = dict(_channel=channel_enum.value)

        params_length = cls.calc_true_item_length(list(params.values()))

        model = cls.query_one(query_fields=query_fields)
        if not model:
            # 新建
            if params_length:
                return cls._create_rule(extra_fields=fields, **params), None
            return None, None

        if params_length == 0:
            # 删除
            cls.commit_models(model, delete=True)
            return None, None

        # 更新
        params['router_id'] = model.router_id
        return cls._update_rule(extra_fields=fields, **params)
