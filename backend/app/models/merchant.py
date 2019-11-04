import copy
import json
import traceback
from operator import attrgetter

from flask import current_app
from sqlalchemy.exc import IntegrityError

from app.enums.account import AccountStateEnum
from app.libs.datetime_kit import DateTimeKit
from app.libs.error_code import SqlIntegrityError
from app.libs.exceptions import InsufficientBalanceException
from app.libs.model.mix import AdminLogMix
from app.models.backoffice.admin_log import AdminLog
from config import MerchantTypeEnum
from app.enums.trade import BalanceTypeEnum, BalanceAdjustTypeEnum, PayMethodEnum, PaymentFeeTypeEnum, PayTypeEnum, \
    OrderSourceEnum, CostTypeEnum
from app.extensions import db
from app.libs.balance_kit import BalanceKit
from app.libs.model.base import ModelBase, MerchantMonthBase
from config import MerchantEnum


class MerchantInfo(AdminLogMix, ModelBase):
    """
    商户基本信息
    """
    admin_log_model = AdminLog

    _merchant = db.Column('merchant', db.Integer, comment="商户", nullable=False, unique=True)
    _bl_type = db.Column('type', db.SmallInteger, comment="商户类型", nullable=False, default=MerchantTypeEnum.NORMAL.value)
    _state = db.Column('state', db.SmallInteger, comment="账号状态", nullable=False, default=AccountStateEnum.ACTIVE.value)

    bl_ava = db.Column(db.BigInteger, comment="可用余额(分钱)", nullable=False, default=0)
    bl_inc = db.Column(db.BigInteger, comment="在途余额(分钱)", nullable=False, default=0)
    bl_fro = db.Column(db.BigInteger, comment="冻结余额(分钱)", nullable=False, default=0)

    @property
    def merchant(self) -> MerchantEnum:
        return MerchantEnum(self._merchant)

    @merchant.setter
    def merchant(self, value: MerchantEnum):
        self._merchant = value.value

    @property
    def m_type(self):
        return MerchantTypeEnum(self._bl_type)

    @m_type.setter
    def m_type(self, value: MerchantTypeEnum):
        self._bl_type = value.value

    @property
    def state(self) -> AccountStateEnum:
        return AccountStateEnum(self._state)

    @state.setter
    def state(self, value: AccountStateEnum):
        self._state = value.value

    @property
    def balance_total(self):
        """
        总余额
        :return:
        """
        return self.balance_available + self.balance_income + self.balance_frozen

    @property
    def balance_available(self):
        """
        可用余额，浮点显示
        :return:
        """
        return BalanceKit.divide_hundred(self.bl_ava)

    @property
    def balance_income(self):
        """
        在途余额，浮点显示
        :return:
        """
        return BalanceKit.divide_hundred(self.bl_inc)

    @property
    def balance_frozen(self):
        """
        冻结余额，浮点显示
        :return:
        """
        return BalanceKit.divide_hundred(self.bl_fro)

    @classmethod
    def create_merchant_models(cls, m_name: MerchantEnum, m_type: MerchantTypeEnum):
        """
        新建商户模型
        :param m_name:
        :param m_type:
        :return:
        """
        models = list()
        params = dict(
            merchant=m_name,
            m_type=m_type,
        )
        merchant = cls.get_model_obj()
        merchant.set_attr(params)
        merchant.set_after_fields(params)
        models.append(merchant)

        log_model = cls.add_admin_log(merchant)
        log_model and models.append(log_model)

        return models

    @classmethod
    def create_merchant(cls, m_name: MerchantEnum, m_type: MerchantTypeEnum):
        """
        新建商户
        :param m_name:
        :param m_type:
        :return:
        """
        models = cls.create_merchant_models(m_name, m_type)
        cls.commit_models(models=models)
        return models[0]

    @classmethod
    def delete_merchant(cls, merchant: MerchantEnum):
        """
        删除商户
        :param merchant:
        :return:
        """
        with db.auto_commit():
            obj = cls.query.filter(cls._merchant == merchant.value).first()
            obj.set_before_fields(['merchant'])

            db.session.delete(obj)

            log_model = cls.add_admin_log(obj)
            log_model and db.session.add(log_model)

    @classmethod
    def query_merchant(cls, m_name: MerchantEnum):
        """
        查询商户
        :param m_name:
        :return:
        """
        return cls.query.filter(cls._merchant == m_name.value).first()


@MerchantMonthBase.init_models
class MerchantBalanceEvent(AdminLogMix, MerchantMonthBase):
    """
    商户余额变更事件表
    """
    __abstract__ = True
    admin_log_model = AdminLog

    _create_time = db.Column('create_time', db.Integer, nullable=False, comment="创建时间", index=True)

    # 当订单表即将要修改订单状态为支付成功时生成ref id，确保订单状态的修改和ref ID的生成原子操作
    ref_id = db.Column(db.String(length=32), comment="票据ID", nullable=False, unique=True)

    _order_type = db.Column('order_type', db.SmallInteger, comment="账变类型", nullable=False, index=True)
    _source = db.Column('source', db.SmallInteger, comment="来源", nullable=False)
    _bl_type = db.Column('bl_type', db.SmallInteger, comment="余额类型", nullable=True)
    value = db.Column(db.Integer, comment="修改数值", nullable=False, default=0)
    _ad_type = db.Column('ad_type', db.SmallInteger, comment="修改数值", nullable=False)

    tx_id = db.Column(db.String(length=32), comment="交易流水号", nullable=False)
    comment = db.Column(db.Text, comment="修改备注信息", nullable=True)

    # json存储
    _extra = db.Column(db.Text, comment="其它附加信息", nullable=True)

    _merchant = db.Column('merchant', db.Integer, comment="商户ID", nullable=False)

    @property
    def merchant(self) -> MerchantEnum:
        return MerchantEnum(self._merchant)

    @merchant.setter
    def merchant(self, merchant: MerchantEnum):
        self._merchant = merchant.value

    @property
    def value_real(self):
        return BalanceKit.divide_hundred(self.value)

    @property
    def source(self) -> OrderSourceEnum:
        return OrderSourceEnum(self._source)

    @source.setter
    def source(self, value: OrderSourceEnum):
        self._source = value.value

    @property
    def order_type(self) -> PayTypeEnum:
        return PayTypeEnum(self._order_type)

    @order_type.setter
    def order_type(self, value: PayTypeEnum):
        self._order_type = value.value

    @property
    def bl_type(self) -> BalanceTypeEnum:
        return BalanceTypeEnum(self._bl_type)

    @bl_type.setter
    def bl_type(self, value: BalanceTypeEnum):
        self._bl_type = value.value

    @property
    def ad_type(self) -> BalanceAdjustTypeEnum:
        return BalanceAdjustTypeEnum(self._ad_type)

    @ad_type.setter
    def ad_type(self, value: BalanceAdjustTypeEnum):
        self._ad_type = value.value

    @property
    def raw_extra(self):
        return self._extra

    @property
    def extra(self) -> dict:
        if self._extra:
            return json.loads(self._extra)

    @extra.setter
    def extra(self, value: dict):
        if value:
            self._extra = json.dumps(value, separators=[',', ':'])

    @classmethod
    def query_event(cls, merchant: MerchantEnum, create_time, ref_id=None, source: OrderSourceEnum = None,
                    order_type: PayTypeEnum = None,
                    bl_type: BalanceTypeEnum = None, ad_type: BalanceAdjustTypeEnum = None,
                    tx_id=None,
                    ):
        """
        查询事件
        :param merchant:
        :param create_time:
        :param source:
        :param order_type:
        :param bl_type:
        :param ad_type:
        :param ref_id:
        :param tx_id:
        :return:
        """
        query_params = dict()

        if source:
            query_params.update(_source=source.value)
        if order_type:
            query_params.update(_order_type=order_type.value)
        if bl_type:
            query_params.update(_bl_type=bl_type.value)
        if ad_type:
            query_params.update(_ad_type=ad_type.value)
        if tx_id:
            query_params.update(tx_id=tx_id)

        if ref_id:
            query_params = dict(ref_id=ref_id)

        if not query_params:
            current_app.config['SENTRY_DSN'] and current_app.logger.fatal('invalid query params: %s', locals())
            return None

        return cls.query_model(query_params, merchant=merchant, date=create_time)

    @classmethod
    def __check_event_params(cls, params):
        """
        参数检查检查
        :param params:
        :return:
        """

        if params['value'] <= 0:
            # 金额不能为负数
            msg = "invalid value, params: %s" % params
            current_app.config['SENTRY_DSN'] and current_app.logger.fatal(msg)
            return -1, msg

        if OrderSourceEnum.MANUALLY != params['source']:
            # 来自订单
            if not params['tx_id']:
                # 如果来源是充值/提款，必须填写系统订单号
                msg = "invalid tx_id, params: %s" % params
                current_app.config['SENTRY_DSN'] and current_app.logger.fatal(msg)
                return -2, msg

            if (params['order_type'] == PayTypeEnum.DEPOSIT and params['ad_type'] == BalanceAdjustTypeEnum.MINUS) or (
                    params['order_type'] == PayTypeEnum.WITHDRAW and params['ad_type'] == BalanceAdjustTypeEnum.PLUS):
                # 不允许提款修改在途余额
                msg = "invalid order_type or ad_type, params: %s" % params
                current_app.config['SENTRY_DSN'] and current_app.logger.fatal(msg)
                return -3, msg

            if params['bl_type'] == BalanceTypeEnum.INCOME and params['order_type'] == PayTypeEnum.WITHDRAW:
                # 不允许提款修改在途余额
                msg = "invalid bl_type or order_type, params: %s" % params
                current_app.config['SENTRY_DSN'] and current_app.logger.fatal(msg)
                return -4, msg

            if params['bl_type'] == BalanceTypeEnum.FROZEN:
                # 冻结余额的变更不能来自订单
                msg = "invalid bl_type, params: %s" % params
                current_app.config['SENTRY_DSN'] and current_app.logger.fatal(msg)
                return -7, msg

        else:
            # 人工调整
            if params['ad_type'] is None or not params['comment']:
                # 人工调整必须填写调整类型和备注
                msg = "invalid ad_type or comment, params: %s" % params
                current_app.config['SENTRY_DSN'] and current_app.logger.fatal(msg)
                return -5, msg

            if params['bl_type'] == BalanceTypeEnum.INCOME and params['ad_type'] == BalanceAdjustTypeEnum.PLUS:
                # 在途余额的增加，是从非D0渠道的订单充值过来的，不能手动去改
                msg = "invalid bl_type or ad_type, params: %s" % params
                current_app.config['SENTRY_DSN'] and current_app.logger.fatal(msg)
                return -6, msg

        return 0, ''

    @classmethod
    def __get_query_merchant(cls, merchant, source, order_type, bl_type, ad_type, value):
        query = MerchantInfo.query.filter(MerchantInfo._merchant == merchant.value)

        update_values = dict()

        if bl_type == BalanceTypeEnum.AVAILABLE:
            update_values.update(bl_ava=MerchantInfo.bl_ava + value)
            if ad_type == BalanceAdjustTypeEnum.MINUS:
                # 确保可用余额不出现负数
                query = query.filter(MerchantInfo.bl_ava >= abs(value))

        elif bl_type == BalanceTypeEnum.INCOME:
            if ad_type == BalanceAdjustTypeEnum.MINUS and (
                    source == OrderSourceEnum.MANUALLY or order_type == PayTypeEnum.FEE):
                # 在途余额的减少，只能来自人工调整，从在途余额中减少，增加到可用余额
                update_values.update(
                    bl_inc=MerchantInfo.bl_inc + value,
                    bl_ava=MerchantInfo.bl_ava - value,
                )
                if ad_type == BalanceAdjustTypeEnum.MINUS:
                    # 确保在途余额不出现负数
                    query = query.filter(MerchantInfo.bl_inc >= abs(value))

            elif ad_type == BalanceAdjustTypeEnum.PLUS and order_type == PayTypeEnum.DEPOSIT:
                # 在途余额的增加，只能来源于非D0渠道的充值订单
                update_values.update(bl_inc=MerchantInfo.bl_inc + value)

        elif bl_type == BalanceTypeEnum.FROZEN:
            # 冻结余额和可用余额是相互转换的关系
            update_values.update(
                bl_fro=MerchantInfo.bl_fro + value,
                bl_ava=MerchantInfo.bl_ava - value,
            )
            # 确保余额不出现负数
            if ad_type == BalanceAdjustTypeEnum.MINUS:
                query = query.filter(MerchantInfo.bl_fro >= abs(value))
            if ad_type == BalanceAdjustTypeEnum.PLUS:
                query = query.filter(MerchantInfo.bl_ava >= abs(value))
        return query, update_values

    @classmethod
    def __update_balance(cls, merchant, source, order_type, bl_type, ad_type, value):
        """
        更新数据库余额
        :param merchant:
        :param source:
        :param order_type: PayTypeEnum.DEPOSIT
        :param bl_type: BalanceTypeEnum  余额类型： 在途（d1,t1）, 可用余额， 冻结
        :param ad_type: BalanceAdjustTypeEnum.PLUS/ BalanceAdjustTypeEnum.MINUS
        :param value:
        :return:
        """
        # 保存修改之前的值
        query, update_values = cls.__get_query_merchant(merchant, source, order_type, bl_type, ad_type, value)
        before_merchant = query.first()
        if not before_merchant:
            # 抛出异常，让事务回滚
            raise InsufficientBalanceException('failed to update balance, query none, query: %s' % str(query))

        before_merchant.set_before_fields(update_values.keys())

        # 修改数据库余额
        query, update_values = cls.__get_query_merchant(merchant, source, order_type, bl_type, ad_type, value)
        count = query.update(
            update_values,
            synchronize_session="evaluate"
        )

        if count != 1:
            # 抛出异常，让事务回滚
            raise RuntimeError('failed to update balance, query: %s' % str(query))

        # 保存修改之后的值
        after_merchant = MerchantInfo.query_by_id(before_merchant.id)
        after_merchant.set_after_fields({k: getattr(after_merchant, k) for k in update_values.keys()})

        return before_merchant, after_merchant

    @classmethod
    def update_balance(cls, merchant: MerchantEnum, ref_id, source: OrderSourceEnum, bl_type: BalanceTypeEnum,
                       value: float, order_type: PayTypeEnum, tx_id,
                       ad_type: BalanceAdjustTypeEnum = None, comment: str = '',
                       create_time=None, commit=True):
        """
        修改余额
        :param merchant:
        :param ref_id: 32位的md5ID
        :param source: 操作来源
        :param order_type: 订单类型
        :param bl_type: 余额类型
        :param ad_type: 当人工操作时，必填调整类型；订单类型的调整不需要填写ad_type
        :param value: 始终传入正整数
        :param comment: 当人工调整时，必填备注信息
        :param create_time:
        :param tx_id: 交易流水号
        :param commit: 是否立即提交事务
        :return: (result, msg)
        """
        # 记录一个参数日志, locals自动收集这行代码之前出现过的局部变量
        params = copy.deepcopy(locals())
        params.pop('cls')

        # current_app.config['SENTRY_DSN'] and current_app.logger.info('update_balance, params: %s', params)

        rst, msg = cls.__check_event_params(params)
        if rst != 0:
            return rst, msg

        if ad_type is None:
            if source == PayTypeEnum.DEPOSIT:
                # 存款+
                ad_type = BalanceAdjustTypeEnum.PLUS
            else:
                # 提款-
                ad_type = BalanceAdjustTypeEnum.MINUS

        # 金额入库乘100转换为分钱
        value = BalanceKit.multiple_hundred(value)

        if ad_type == BalanceAdjustTypeEnum.MINUS:
            # 做减法
            value = -value

        try:
            with db.auto_commit(commit):
                # 生成修改事件
                create_time = create_time or DateTimeKit.get_cur_datetime()
                fields = dict(
                    source=source,
                    order_type=order_type,
                    bl_type=bl_type,
                    value=value,
                    tx_id=tx_id,
                    ad_type=ad_type,
                    comment=comment,
                    ref_id=ref_id,
                    create_time=create_time,
                    extra=dict(),
                )
                rst = cls.add_model(fields, merchant=merchant, date=create_time)
                db.session.add(rst['model'])

                # 更新商户余额
                before_merchant, after_merchant = cls.__update_balance(merchant, source, order_type, bl_type, ad_type,
                                                                       value)
                # 添加admin日志
                if source == OrderSourceEnum.MANUALLY:
                    log_model = cls.add_admin_log(
                        data_before=before_merchant.get_before_fields(),
                        data_after=after_merchant.get_after_fields(),
                    )
                    log_model and db.session.add(log_model)

        except RuntimeError as e:
            # 捕获异常，返回失败
            msg = "%s, params: %s" % (str(e), params)
            current_app.config['SENTRY_DSN'] and current_app.logger.fatal(msg)
            return -100, str(e)

        except InsufficientBalanceException as e:
            msg = str(e)
            if bl_type == BalanceTypeEnum.AVAILABLE:
                msg = "可用余额不足"
            if bl_type == BalanceTypeEnum.INCOME:
                msg = "在途余额不足"
            if bl_type == BalanceTypeEnum.FROZEN:
                if ad_type == BalanceAdjustTypeEnum.PLUS:
                    msg = "可用余额不足"
                else:
                    msg = "冻结余额不足"
            return -101, msg

        return 0, ''


class MerchantFeeConfig(AdminLogMix, ModelBase):
    """
    商户费率控制
    """
    admin_log_model = AdminLog

    _merchant = db.Column('merchant', db.Integer, comment="商户", nullable=False)
    version = db.Column(db.Integer, comment="版本", nullable=False, default=1)
    valid = db.Column(db.SmallInteger, comment="是否被删除的标记", nullable=False)

    _p_way = db.Column('p_way', db.SmallInteger, comment="支付形式", nullable=False)
    _p_method = db.Column('p_method', db.SmallInteger, comment="支付方法", nullable=False, default=0)
    _fee_type = db.Column('fee_type', db.SmallInteger, comment="费用类型", nullable=False,
                          default=PaymentFeeTypeEnum.PERCENT_PER_ORDER.value)
    _value = db.Column('value', db.Integer, comment="值", nullable=False, default=0)
    _cost_type = db.Column('cost_type', db.Integer, comment="扣费类型", nullable=True)

    __table_args__ = (
        # 联合唯一索引
        db.UniqueConstraint('merchant', 'version', 'valid', 'p_way', 'p_method',
                            name='uix_merchant_fee_version_valid_way_method'),
    )

    @property
    def short_description(self):
        s = 'version: ' + str(self.version) + ', ' + (
            self.payment_method.desc if self.payment_method else '') + \
            self.value_description + "(" + self.cost_type.desc + ")"
        return s

    @property
    def config_id(self):
        return self.id

    @property
    def merchant(self) -> MerchantEnum:
        return MerchantEnum(self._merchant)

    @merchant.setter
    def merchant(self, value: MerchantEnum):
        self._merchant = value.value

    @property
    def cost_type(self) -> CostTypeEnum:
        if not self._cost_type:
            return CostTypeEnum.MERCHANT
        return CostTypeEnum(self._cost_type)

    @cost_type.setter
    def cost_type(self, value: CostTypeEnum):
        self._cost_type = value.value

    @property
    def payment_way(self) -> PayTypeEnum:
        return PayTypeEnum(self._p_way)

    @payment_way.setter
    def payment_way(self, value: PayTypeEnum):
        self._p_way = value.value

    @property
    def payment_method(self) -> PayMethodEnum:
        if self._p_method:
            return PayMethodEnum(self._p_method)

    @payment_method.setter
    def payment_method(self, value: PayMethodEnum):
        if value:
            self._p_method = value.value

    @property
    def fee_type(self) -> PaymentFeeTypeEnum:
        return PaymentFeeTypeEnum(self._fee_type)

    @fee_type.setter
    def fee_type(self, value: PaymentFeeTypeEnum):
        self._fee_type = value.value

    @property
    def value(self):
        return BalanceKit.divide_hundred(self._value)

    @value.setter
    def value(self, value):
        self._value = BalanceKit.multiple_hundred(value)

    @property
    def value_description(self):
        return "{}{}".format(self.value, self.fee_type.desc)

    @classmethod
    def convert_query_fields(cls, query_fields):
        params = dict(
            _merchant=query_fields['merchant'].value
        )
        if query_fields.get('payment_way'):
            params['_p_way'] = query_fields['payment_way'].value
        if query_fields.get('payment_method'):
            params['_p_method'] = query_fields['payment_method'].value
        return params

    @classmethod
    def query_latest_one(cls, query_fields):
        """
        以version倒序,查询最新的一个配置
        :param query_fields:
        :return:
        """
        params = cls.convert_query_fields(query_fields)
        return cls.query_one_order_by(query_fields=params, order_fields=[cls.version.desc()])

    @classmethod
    def query_by_config_id(cls, config_id):
        """
        根据主键查询配置
        :param config_id:
        :return:
        """
        return cls.query_by_id(config_id)

    @classmethod
    def query_active_configs(cls, query_fields):
        """
        查询有效的配置
        :param query_fields:
        :return:
        """
        params = cls.convert_query_fields(query_fields)
        params['valid'] = cls.VALID
        return cls.query_model(params)

    @classmethod
    def update_fee_config(cls, merchant, params: list, models=None):
        """
        修改费率，批量操作
        :param merchant:
        :param params: [
            dict(merchant, payment_way, fee_type, value, payment_method),
            dict(merchant, payment_way, fee_type, value, payment_method),
        ]
        :param models: 商户和日志模型
        :return:
        """
        models = models or list()

        params_dict = cls.get_update_dict(params)
        all_configs = cls.query_active_configs(dict(merchant=merchant))
        for item in all_configs.all():
            if item.item_key not in params_dict:
                # 不在更新列表里面的，全部标记为删除
                item.valid = cls.INVALID
                models.append(item)

        for fields in params:
            fields = copy.deepcopy(fields)
            fields['valid'] = cls.VALID
            model = cls.query_latest_one(dict(
                merchant=fields.get('merchant'),
                payment_way=fields.get('payment_way'),
                payment_method=fields.get('payment_method', None),
            ))
            if model:
                fields['version'] = model.version + 1
            else:
                fields['version'] = 1

            rst = cls.add_model(fields=fields)
            models.append(rst['model'])

            log_model = cls.add_admin_log(rst['model'])
            log_model and models.append(log_model)

        try:
            cls.commit_models(models=models)
        except IntegrityError as e:
            print(e)
            current_app.config['SENTRY_DSN'] and current_app.logger.fatal(traceback.format_exc())
            return False, SqlIntegrityError()

        return True, None

    @classmethod
    def filter_latest_items(cls, items):
        """
        过滤出最新的配置，同一个渠道下的旧的配置会被排除掉
        :param items:
        :return:
        """
        # 按version值倒序，version值越大，记录越新
        items = sorted(items, key=attrgetter('version'), reverse=True)

        latest = dict()

        for item in items:
            if not item.valid:
                # 已经删除的过滤掉
                continue
            key = item.item_key
            if key in latest:
                # 已经存在的配置直接跳过
                continue
            latest[key] = item

        return latest.values()

    @property
    def item_key(self):
        """
        唯一键
        :return:
        """
        return self._merchant, self._p_way, self._p_method

    @classmethod
    def get_update_dict(cls, update_list: list):
        tmp = dict()

        for fields in update_list:
            params = cls.convert_query_fields(fields)
            tmp[(params['_merchant'], params['_p_way'], params.get('_p_method'))] = fields

        return tmp

    @classmethod
    def get_latest_active_configs(cls, merchant, payment_way):
        """
        获取商户最新的有效的费率配置
        :param merchant:
        :param payment_way:
        :return:
        """
        merchant_fees = MerchantFeeConfig.query_active_configs(query_fields=dict(
            merchant=merchant,
            payment_way=payment_way,
        )).all()
        return MerchantFeeConfig.filter_latest_items(merchant_fees)
