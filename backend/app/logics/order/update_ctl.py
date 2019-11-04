import copy
import traceback

from flask import current_app

from app.enums.trade import PayTypeEnum, OrderStateEnum, SettleStateEnum, DeliverStateEnum, DeliverTypeEnum, \
    OrderSourceEnum, PayMethodEnum
from app.libs.datetime_kit import DateTimeKit
from app.libs.model.mix import ModelOpMix
from app.models.order.order import OrderWithdraw, OrderDeposit
from app.models.order.order_blobal import GlobalOrderId, OrderConstraint
from app.models.order.order_detail import OrderDetailDeposit, OrderDetailWithdraw
from app.models.order.order_event import OrderEvent
from config import MerchantEnum


class OrderUpdateCtl:

    @classmethod
    def __update_order(cls, **kwargs):
        fields = dict(
            update_time=kwargs['update_time'],
        )

        if kwargs['state']:
            fields.update(state=kwargs['state'])
        if kwargs['channel_id']:
            fields.update(channel_id=kwargs['channel_id'])
        if kwargs['mch_fee_id']:
            fields.update(mch_fee_id=kwargs['mch_fee_id'])
        if kwargs['tx_amount']:
            fields.update(tx_amount=kwargs['tx_amount'])
        if kwargs['channel_tx_id']:
            fields.update(channel_tx_id=kwargs['channel_tx_id'])
        if kwargs['settle']:
            fields.update(settle=kwargs['settle'])
        if kwargs['deliver']:
            fields.update(deliver=kwargs['deliver'])
        if kwargs['pay_method']:
            fields.update(pay_method=kwargs['pay_method'])

        if kwargs['order_type'] == PayTypeEnum.DEPOSIT:
            order_cls = OrderDeposit
        else:
            order_cls = OrderWithdraw

        return order_cls.update_model(
            fields=fields,
            query_fields=dict(id=kwargs['order_id']),
            merchant=kwargs['merchant'],
            date=kwargs['create_time'],
        ), fields

    @classmethod
    def __update_order_detail(cls, **kwargs):
        fields = dict()

        if kwargs['offer']:
            fields.update(offer=kwargs['offer'])
        if kwargs['fee']:
            fields.update(fee=kwargs['fee'])
        if kwargs['cost']:
            fields.update(cost=kwargs['cost'])
        if kwargs['profit']:
            fields.update(profit=kwargs['profit'])
        if kwargs['tx_amount']:
            fields.update(tx_amount=kwargs['tx_amount'])
        if kwargs['done_time']:
            fields.update(done_time=kwargs['done_time'])
        if kwargs['comment']:
            fields.update(comment=kwargs['comment'])
        if kwargs['op_account']:
            fields.update(op_account=kwargs['op_account'])

        if kwargs['order_type'] == PayTypeEnum.DEPOSIT:
            order_cls = OrderDetailDeposit

        else:
            order_cls = OrderDetailWithdraw

            if kwargs['deliver_type']:
                fields.update(deliver_type=kwargs['deliver_type'])
            if kwargs['alloc_time']:
                fields.update(alloc_time=kwargs['alloc_time'])
            if kwargs['deal_time']:
                fields.update(deal_time=kwargs['deal_time'])

        return order_cls.update_model(
            fields=fields,
            query_fields=dict(id=kwargs['order_id']),
            merchant=kwargs['merchant'],
            date=kwargs['create_time'],
        ), fields

    @classmethod
    def __create_event(cls, **kwargs):

        fields = dict(
            create_time=kwargs['create_time'],
            uid=kwargs['uid'],
            order_id=kwargs['order_id'],
            ref_id=kwargs['ref_id'],
        )

        return OrderEvent.add_model(fields, merchant=kwargs['merchant'], date=kwargs['create_time'])

    @classmethod
    def update_order_event(
            cls,
            order_id,
            uid,
            merchant: MerchantEnum,
            state: OrderStateEnum = None,  # 订单状态
            tx_amount=0,  # 实际支付金额
            pay_method: PayMethodEnum = None,  # 支付方法
            ref_id=None,  # 票据ID
            channel_tx_id=None,  # 通道交易ID，支付成功后填写
            settle: SettleStateEnum = None,  # 结算状态
            deliver: DeliverStateEnum = None,  # 给下游商户的发货（通知）状态
            channel_id: int = None,  # 通道费率ID，ABSChannelConfig 表中的主键ID，确认出款时必填
            mch_fee_id: int = None,  # 商户费率配置ID，MerchantFeeConfig 表的主键ID，确认出款时必填
            op_account=None,  # 后台管理员账号
            comment=None,  # 管理后台修改备注
            offer=None,  # 优惠金额
            fee=None,  # 手续费
            cost=None,  # 成本金额
            profit=None,  # 利润（收入）金额
            deliver_type: DeliverTypeEnum = None,  # 出款类型
            alloc_time=None,  # 提款订单分配时间
            deal_time=None,  # 提款订单处理时间
            done_time=None,  # 订单完成时间
            commit=True,  # 是否立即提交事务
    ):
        update_time = DateTimeKit.get_cur_datetime()
        g_order_id = GlobalOrderId.query_global_id(order_id)
        create_time = g_order_id.create_time
        order_type = g_order_id.order_type

        if order_type == PayTypeEnum.WITHDRAW:
            if state == OrderStateEnum.DEALING:
                if deliver_type == DeliverTypeEnum.MANUALLY:
                    if not (mch_fee_id and deal_time):
                        raise RuntimeError("人工出款时必填 mch_fee_id/deal_time")
                else:
                    if not deal_time:
                        raise RuntimeError("出款时必填 deal_time")
            if state == OrderStateEnum.ALLOC and not alloc_time:
                raise RuntimeError("认领订单必填认领时间")

        elif order_type == PayTypeEnum.DEPOSIT:
            pass

        if state in [OrderStateEnum.SUCCESS, OrderStateEnum.FAIL] and not done_time:
            # 订单交易完成
            done_time = update_time

        params = copy.deepcopy(locals())
        params.pop('cls')

        if not ref_id:
            ref_id = OrderConstraint.apply_ref_id(order_id, order_type, state)
            if not ref_id:
                # 票据申请失败
                return None, ref_id
            params['ref_id'] = ref_id

        try:
            # 订单事件
            rst = cls.__create_event(**params)
            order_event = rst['model']

            rst, fields = cls.__update_order(**params)
            if rst['code'] != 0:
                OrderConstraint.revoke_order_state(order_id, state)
                current_app.logger.error('rst: %s, params: %s', rst, params)
                return None, ''

            models = list(rst['model'].values())
            order = rst['model']['hot']

            # 订单详情
            rst, fields = cls.__update_order_detail(**params)
            if rst['code'] != 0:
                OrderConstraint.revoke_order_state(order_id, state)
                current_app.logger.error('rst: %s, params: %s', rst, params)
                return None, ''

            models.extend(rst['model'].values())
            order_detail = rst['model']['hot']

            # 订单修改事件
            rst = cls.__create_event(**params)
            order_event = rst['model']
            order_event.data_before = [order.get_before_fields(), order_detail.get_before_fields()]
            order_event.data_after = [order.get_after_fields(), order_detail.get_after_fields()]
            models.append(order_event)

            # 提交事务
            assert len(models) == 5
            ModelOpMix.commit_models(models=models, commit=commit)

        except Exception as e:
            # 任何非期望的异常都要回滚状态
            OrderConstraint.revoke_order_state(order_id, state)
            current_app.logger.error(traceback.format_exc())
            return None, ref_id

        return order, ref_id
