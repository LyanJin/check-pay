import copy

from flask import current_app

from app.enums.trade import PayTypeEnum, OrderStateEnum
from app.extensions import db
from app.libs.model.base import ModelBase
from app.libs.order_kit import OrderUtils
from config import MerchantEnum


class GlobalOrderId(ModelBase):
    """
    生成订单ID，与其它索引键建立映射关系
    """
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True, comment='自增主键')
    uid = db.Column(db.Integer, comment='用户ID', nullable=False)
    _order_type = db.Column('order_type', db.SmallInteger, comment="订单类型", nullable=False)
    _merchant = db.Column('merchant', db.Integer, comment="商户", nullable=False)

    @property
    def order_id(self):
        return self.id

    @order_id.setter
    def order_id(self, value):
        self.id = value

    @property
    def order_type(self) -> PayTypeEnum:
        return PayTypeEnum(self._order_type)

    @order_type.setter
    def order_type(self, value: PayTypeEnum):
        self._order_type = value.value

    @property
    def merchant(self) -> MerchantEnum:
        return MerchantEnum(self._merchant)

    @merchant.setter
    def merchant(self, value: MerchantEnum):
        self._merchant = value.value

    @classmethod
    def generate_order_id(cls, uid, order_type, create_time, merchant):
        obj = cls()
        obj.uid = uid
        obj.order_type = order_type
        obj.create_time = create_time
        obj.merchant = merchant
        cls.commit_models(obj)
        return obj.order_id

    @classmethod
    def query_global_id(cls, order_id):
        return cls.query.filter_by(id=order_id).first()

    @classmethod
    def query_latest_one(cls, uid=None, order_type=None):
        q_params = dict()
        if uid:
            q_params['uid'] = uid
        if order_type:
            q_params['_order_type'] = order_type.value
        return cls.query.filter_by(**q_params).order_by(cls.id.desc()).first()


class OrderConstraint(ModelBase):
    """
    订单状态唯一约束
    """
    order_id = db.Column(db.Integer, comment='订单ID', nullable=False)
    _state = db.Column('state', db.SmallInteger, comment="订单状态", nullable=False)

    __table_args__ = (
        # 联合唯一索引
        db.UniqueConstraint('order_id', 'state', name='uix_order_constraint_order_id_state'),
    )

    @property
    def state(self) -> OrderStateEnum:
        return OrderStateEnum(self._state)

    @state.setter
    def state(self, value: OrderStateEnum):
        self._state = value.value

    @classmethod
    def query_by_order_id(cls, order_id):
        return cls.query_one(dict(order_id=order_id))

    @classmethod
    def revoke_order_state(cls, order_id, state: OrderStateEnum):
        """
        回滚订单状态
        :param order_id:
        :param state:
        :return:
        """
        if not state:
            return

        cls.get_model_cls().query.filter_by(order_id=order_id).update(dict(_state=state.value))

    @classmethod
    def apply_ref_id(cls, order_id, order_type: PayTypeEnum, state: OrderStateEnum):
        """
        申请修改订单的票据ID
        :param order_id:
        :param order_type:
        :param state:
        :return:
        """
        if not state:
            return OrderUtils.gen_unique_ref_id()

        params = copy.deepcopy(locals())
        params.pop('cls')

        if state == OrderStateEnum.INIT:
            # 初始化状态无需前置状态约束
            model = cls.get_model_obj()
            model.order_id = order_id
            model.state = state
            model.commit_models(model)
            return OrderUtils.gen_unique_ref_id()

        query_params = dict(
            order_id=order_id,
        )

        if order_type == PayTypeEnum.WITHDRAW:
            if state == OrderStateEnum.ALLOC:
                query_params.update(_state=OrderStateEnum.INIT.value)
            elif state == OrderStateEnum.DEALING:
                query_params.update(_state=OrderStateEnum.ALLOC.value)
            elif state == OrderStateEnum.SUCCESS:
                query_params.update(_state=OrderStateEnum.DEALING.value)
            elif state == OrderStateEnum.FAIL:
                # 状态变更为失败，无需前置状态约束
                pass
            else:
                raise ValueError('invalid state, params: %s' % params)

        elif order_type == PayTypeEnum.DEPOSIT:
            if state == OrderStateEnum.SUCCESS:
                query_params.update(_state=OrderStateEnum.INIT.value)
            elif state == OrderStateEnum.FAIL:
                # 状态变更为失败，无需前置状态约束
                pass
            else:
                raise ValueError('invalid state, params: %s' % params)

        elif order_type == PayTypeEnum.DEPOSIT:
            if state == OrderStateEnum.FAIL:
                # 只有状态成功后才有退款
                query_params.update(_state=OrderStateEnum.SUCCESS.value)
            else:
                raise ValueError('invalid state, params: %s' % params)

        # 让数据库来确保事务
        with db.auto_commit():
            effect = cls.get_model_cls().query.filter_by(**query_params).update(dict(_state=state.value))
            if effect != 1:
                msg = '修改订单状态的票据ID申请失败，query_params: %s, params: %s' % (query_params, params)
                current_app.config['SENTRY_DSN'] and current_app.logger.error(msg)
                return None

        return OrderUtils.gen_unique_ref_id()
