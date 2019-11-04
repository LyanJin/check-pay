import copy
import json

from flask import current_app

from app.enums.trade import PayTypeEnum, BalanceAdjustTypeEnum, BalanceTypeEnum, OrderSourceEnum
from app.extensions import db
from app.libs.balance_kit import BalanceKit
from app.libs.datetime_kit import DateTimeKit
from app.libs.exceptions import InsufficientBalanceException
from app.libs.model.base import MerchantMonthBase, MerchantBase
from app.libs.model.mix import AdminLogMix
from app.libs.string_kit import PhoneNumberParser
from app.models.backoffice.admin_log import AdminLog
from config import MerchantEnum
from app.libs.order_kit import OrderUtils


# @MerchantBase.init_models
class UserBalance(MerchantBase):
    """
    用户余额，按商户分库
    """
    # __abstract__ = True

    id = db.Column(db.Integer, primary_key=True, autoincrement=False, comment='用户ID')
    balance = db.Column(db.BigInteger, comment="余额(分钱)", nullable=False, default=0)

    _merchant = db.Column('merchant', db.Integer, comment="商户ID", nullable=False)

    @property
    def merchant(self) -> MerchantEnum:
        return MerchantEnum(self._merchant)

    @merchant.setter
    def merchant(self, merchant: MerchantEnum):
        self._merchant = merchant.value

    @property
    def real_balance(self):
        return BalanceKit.divide_hundred(self.balance)

    @property
    def uid(self):
        return self.id

    @uid.setter
    def uid(self, value):
        self.id = value

    @classmethod
    def generate_model(cls, uid, merchant: MerchantEnum):
        balance = cls.get_model_obj(merchant=merchant)
        balance.uid = uid
        balance.balance = 0
        balance.merchant = merchant
        return balance

    @classmethod
    def create_user_balance(cls, uid, merchant: MerchantEnum):
        with db.auto_commit():
            balance = cls.generate_model(uid, merchant)
            db.session.add(balance)

    @classmethod
    def query_balance(cls, uid, merchant):
        return cls.query_model(query_fields=dict(id=uid), merchant=merchant)


@MerchantMonthBase.init_models
class UserBalanceEvent(AdminLogMix, MerchantMonthBase):
    """
    用户余额变更事件表
    """
    __abstract__ = True
    admin_log_model = AdminLog

    _create_time = db.Column('create_time', db.Integer, nullable=False, comment="创建时间", index=True)

    uid = db.Column(db.Integer, comment='用户ID', nullable=False)
    _order_type = db.Column('order_type', db.SmallInteger, comment="账变类型", nullable=False)

    # 当订单表即将要修改订单状态为支付成功时生成ref id，确保订单状态的修改和ref ID的生成原子操作
    ref_id = db.Column(db.String(length=32), comment="票据ID", nullable=False, unique=True)

    _source = db.Column('source', db.SmallInteger, comment="来源", nullable=False)
    _bl_type = db.Column('bl_type', db.SmallInteger, comment="余额类型", nullable=False)
    value = db.Column(db.Integer, comment="修改数值", nullable=False, default=0)
    _ad_type = db.Column('ad_type', db.SmallInteger, comment="修改类型", nullable=False)
    # 交易流水号
    tx_id = db.Column(db.String(length=32), comment="交易流水号", nullable=False)

    comment = db.Column(db.Text, comment="修改备注信息", nullable=True)

    # json存储
    _extra = db.Column(db.Text, comment="其它附加信息", nullable=True)

    UNION_INDEX = [('uid', 'order_type')]

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

    @property
    def out_account(self):
        extra = self.extra
        if extra:
            return extra.get('out_account')
        return ''

    @property
    def in_account(self):
        extra = self.extra
        if extra:
            return extra.get('in_account')
        return ''

    @property
    def mask_out_account(self):
        try:
            return PhoneNumberParser.hide_number(self.out_account)
        except:
            return self.out_account

    @property
    def mask_in_account(self):
        try:
            return PhoneNumberParser.hide_number(self.in_account)
        except:
            return self.in_account

    @property
    def order_type(self) -> PayTypeEnum:
        if self._order_type:
            return PayTypeEnum(self._order_type)

    @order_type.setter
    def order_type(self, value: PayTypeEnum):
        if value:
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

    @classmethod
    def query_by_order_types(cls, uid, order_types, merchant: MerchantEnum, date):
        """
        多个账户变动类型一起查询
        :return:
        """
        model_cls = cls.get_model_cls(merchant=merchant, date=date)
        values = [x.value for x in order_types]
        return model_cls.query.filter(model_cls._order_type.in_(values)).filter(model_cls.uid == uid)

    @classmethod
    def query_event(cls, uid, merchant: MerchantEnum, date, source: OrderSourceEnum = None,
                    order_type: PayTypeEnum = None,
                    bl_type: BalanceTypeEnum = None, ad_type: BalanceAdjustTypeEnum = None,
                    ref_id=None, tx_id=None):
        """
        查询事件
        :param merchant: 分库必填字段
        :param uid: 分表必填字段
        :param date:
        :param source:
        :param order_type:
        :param bl_type:
        :param ad_type:
        :param ref_id: 唯一索引
        :param tx_id: 交易流水号
        :return:
        """
        query_params = dict()

        # uid和order_type有联合索引，要利用好
        if uid:
            query_params.update(uid=uid)
        if order_type:
            query_params.update(_order_type=order_type.value)

        if source:
            query_params.update(_source=source.value)
        if bl_type:
            query_params.update(_bl_type=bl_type.value)
        if ad_type:
            query_params.update(_ad_type=ad_type.value)
        if tx_id:
            query_params.update(tx_id=tx_id)

        if ref_id:
            query_params = dict(ref_id=ref_id)

        if not query_params:
            current_app.config['SENTRY_DSN'] and current_app.logger.fatal(
                'invalid query params: %s', locals())
            return None

        return cls.query_model(query_params, merchant=merchant, date=date)

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
            # 来自用户操作
            if params['order_type'] == PayTypeEnum.TRANSFER:
                # 来自用户转账
                pass
            else:
                if (params['order_type'] == PayTypeEnum.DEPOSIT and
                    params['ad_type'] == BalanceAdjustTypeEnum.MINUS) or (
                        params['order_type'] == PayTypeEnum.WITHDRAW and
                        params['ad_type'] == BalanceAdjustTypeEnum.PLUS):
                    # 不允许提款修改在途余额
                    msg = "invalid order_type or ad_type, params: %s" % params
                    current_app.config['SENTRY_DSN'] and current_app.logger.fatal(
                        msg)
                    return -3, msg

        else:
            # 后台人工调整
            if params['ad_type'] is None or not params['comment']:
                # 人工调整必须填写调整类型和备注
                msg = "invalid ad_type or comment, params: %s" % params
                current_app.config['SENTRY_DSN'] and current_app.logger.fatal(
                    msg)
                return -4, msg

        return 0, ''

    @classmethod
    def __get_query_balance(cls, uid, merchant, ad_type, value):
        model = UserBalance.get_model_cls(merchant=merchant, column=uid)
        query = UserBalance.query_balance(uid, merchant)

        update_values = dict(balance=model.balance + value)

        if ad_type == BalanceAdjustTypeEnum.MINUS:
            # 确保可用余额不出现负数
            query = query.filter(model.balance >= abs(value))

        return query, update_values

    @classmethod
    def __update_balance(cls, uid, merchant, ad_type, value):
        """
        更新数据库余额
        :param uid:
        :param ad_type:
        :param value:
        :return:
        """
        # 保存修改之前的值
        query, update_values = cls.__get_query_balance(
            uid, merchant, ad_type, value)
        balance_before = query.first()
        if not balance_before:
            # 抛出异常，让事务回滚
            raise InsufficientBalanceException(
                'failed to update balance, query none, query: %s' % str(query))

        balance_before.set_before_fields(update_values.keys())

        # 修改数据库余额
        query, update_values = cls.__get_query_balance(
            uid, merchant, ad_type, value)
        count = query.update(
            update_values,
            synchronize_session="evaluate"
        )

        if count != 1:
            # 抛出异常，让事务回滚
            raise RuntimeError(
                'failed to update balance, query: %s' % str(query))

        # 保存修改之后的值
        balance_after = UserBalance.query_balance(uid, merchant).first()
        balance_after.set_after_fields(
            {k: getattr(balance_after, k) for k in update_values.keys()})

        return balance_before, balance_after

    @classmethod
    def update_user_balance(cls, uid, merchant: MerchantEnum, ref_id, tx_id, source: OrderSourceEnum,
                            bl_type: BalanceTypeEnum, value: float, order_type: PayTypeEnum,
                            ad_type: BalanceAdjustTypeEnum = None,
                            comment: str = '', create_time=None,
                            in_account=None, out_account=None,
                            commit=True):
        """
        修改余额
        :param uid:
        :param merchant:
        :param create_time:
        :param ref_id: 32位的md5ID
        :param source: 操作来源
        :param order_type: 修改类型，必填
        :param bl_type: 余额类型
        :param ad_type: 当人工操作时，必填调整类型；订单类型的调整不需要填写ad_type
        :param value: 始终传入正整数
        :param comment: 当人工调整时，必填备注信息
        :param tx_id: 交易流水号
        :param in_account: 进账账号
        :param out_account: 出账账号
        :param commit: 是否提交事务
        :return: (result, msg)
        """
        if uid == 0:
            # uid为0，说明不用更新用户余额
            return 0, ''

        # 记录一个参数日志, locals自动收集这行代码之前出现过的局部变量
        params = copy.deepcopy(locals())
        params.pop('cls')

        # current_app.config['SENTRY_DSN'] and current_app.logger.error('update_balance, params: %s', params)

        rst, msg = cls.__check_event_params(params)
        if rst != 0:
            return rst, msg

        if ad_type is None:
            if order_type == PayTypeEnum.DEPOSIT:
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
                    uid=uid,
                    source=source,
                    order_type=order_type,
                    bl_type=bl_type,
                    value=value,
                    ad_type=ad_type,
                    comment=comment,
                    ref_id=ref_id,
                    tx_id=tx_id,
                    create_time=create_time,
                    extra=dict(),
                )
                if in_account:
                    fields['extra'].update(in_account=in_account)
                if out_account:
                    fields['extra'].update(out_account=out_account)

                rst = cls.add_model(fields, merchant=merchant, date=create_time)
                db.session.add(rst['model'])

                # 更新商户余额
                balance_before, balance_after = cls.__update_balance(
                    uid, merchant, ad_type, value)

                # 添加admin日志
                if source == OrderSourceEnum.MANUALLY:
                    log_model = cls.add_admin_log(
                        data_before=balance_before.get_before_fields(),
                        data_after=balance_after.get_after_fields(),
                    )
                    log_model and db.session.add(log_model)

        except RuntimeError as e:
            # 捕获异常，返回失败
            msg = "%s, params: %s" % (str(e), params)
            current_app.config['SENTRY_DSN'] and current_app.logger.fatal(msg)
            return -100, msg

        except InsufficientBalanceException as e:
            msg = "%s, params: %s" % (str(e), params)
            current_app.config['SENTRY_DSN'] and current_app.logger.fatal(msg)
            return -101, '余额不足'

        return 0, ''

    @classmethod
    def transfer(cls, from_user, to_user, merchant: MerchantEnum, amount, comment: str = ''):
        """
        转账
        ref_id = OrderUtils.gen_unique_ref_id()
        PayTypeEnum.TRANSFER
        商户类型是TEST，那么source就是 TEST
        否则是 ONLINE
        """
        from app.models.user import UserBindInfo

        # 记录一个参数日志, locals自动收集这行代码之前出现过的局部变量
        params = copy.deepcopy(locals())
        params.pop('cls')

        try:
            with db.auto_commit(True):

                # 构造source的值
                if merchant.is_test:
                    source = OrderSourceEnum.TESTING
                else:
                    source = OrderSourceEnum.ONLINE

                ref_id_a = OrderUtils.gen_unique_ref_id()
                ref_id_b = OrderUtils.gen_unique_ref_id()
                tx_id = OrderUtils.gen_normal_tx_id(from_user.uid)

                in_bind = UserBindInfo.query_bind_by_uid(to_user.uid)
                if in_bind:
                    in_account = in_bind.name
                else:
                    in_account = to_user.account

                out_bind = UserBindInfo.query_bind_by_uid(from_user.uid)
                if out_bind:
                    out_account = out_bind.name
                else:
                    out_account = from_user.account

                # A用户扣钱
                flag_a, msg_b = cls.update_user_balance(from_user.uid, merchant,
                                                        ref_id=ref_id_a,
                                                        source=source,
                                                        order_type=PayTypeEnum.TRANSFER,
                                                        value=amount,
                                                        bl_type=BalanceTypeEnum.AVAILABLE,
                                                        ad_type=BalanceAdjustTypeEnum.MINUS,
                                                        comment=comment,
                                                        tx_id=tx_id,
                                                        in_account=in_account,
                                                        out_account=out_account,
                                                        commit=False,
                                                        )

                if flag_a != 0:
                    raise RuntimeError(msg_b)

                # B用户加钱
                flag_b, msg_b = cls.update_user_balance(to_user.uid, merchant,
                                                        ref_id=ref_id_b,
                                                        source=source,
                                                        order_type=PayTypeEnum.TRANSFER,
                                                        value=amount,
                                                        bl_type=BalanceTypeEnum.AVAILABLE,
                                                        ad_type=BalanceAdjustTypeEnum.PLUS,
                                                        comment=comment,
                                                        tx_id=tx_id,
                                                        in_account=in_account,
                                                        out_account=out_account,
                                                        commit=False,
                                                        )

                if flag_b != 0:
                    raise RuntimeError(msg_b)

        except RuntimeError as e:
            # 捕获异常，返回失败
            msg = "%s, params: %s" % (str(e), params)
            current_app.config['SENTRY_DSN'] and current_app.logger.fatal(msg)
            return -100, msg

        return True, ''
