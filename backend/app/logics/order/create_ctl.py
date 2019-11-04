import copy

from flask import current_app
from sqlalchemy.exc import IntegrityError

from app.enums.trade import PayTypeEnum, OrderStateEnum, InterfaceTypeEnum, OrderSourceEnum, PayMethodEnum
from app.libs.datetime_kit import DateTimeKit
from app.libs.model.mix import ModelOpMix
from app.libs.order_kit import OrderUtils
from app.models.order.order import OrderDeposit, OrderWithdraw
from app.models.order.order_blobal import GlobalOrderId, OrderConstraint
from app.models.order.order_detail import OrderDetailDeposit, OrderDetailWithdraw
from app.models.order.order_event import OrderEvent
from config import MerchantEnum


class OrderCreateCtl:

    @classmethod
    def __create_order(cls, **kwargs):
        fields = dict(
            uid=kwargs['uid'],
            create_time=kwargs['create_time'],
            update_time=kwargs['create_time'],
            order_id=kwargs['order_id'],
            amount=kwargs['amount'],
            mch_tx_id=kwargs['mch_tx_id'],
            sys_tx_id=kwargs['sys_tx_id'],
            source=kwargs['source'],
            state=OrderStateEnum.INIT,
        )
        if kwargs['channel_id']:
            fields.update(channel_id=kwargs['channel_id'])
        if kwargs['mch_fee_id']:
            fields.update(mch_fee_id=kwargs['mch_fee_id'])
        if kwargs['op_account']:
            fields.update(op_account=kwargs['op_account'])
        if kwargs['pay_method']:
            fields.update(pay_method=kwargs['pay_method'])

        if kwargs['notify_url']:
            fields.update(notify_url=kwargs['notify_url'])
        if kwargs['extra']:
            fields.update(extra=kwargs['extra'])

        if kwargs['order_type'] == PayTypeEnum.DEPOSIT:
            order_cls = OrderDeposit

            if kwargs['result_url']:
                fields.update(result_url=kwargs['result_url'])
        else:
            order_cls = OrderWithdraw

            if kwargs['op_account']:
                fields.update(op_account=kwargs['op_account'])
            if kwargs['bank_id']:
                fields.update(bank_id=kwargs['bank_id'])
            if kwargs['bank_info']:
                fields.update(bank_info=kwargs['bank_info'])

        return order_cls.add_model(fields, merchant=kwargs['merchant'], date=kwargs['create_time']), fields

    @classmethod
    def __create_order_detail(cls, **kwargs):
        fields = dict(
            uid=kwargs['uid'],
            order_id=kwargs['order_id'],
            amount=kwargs['amount'],
            source=kwargs['source'],
            in_type=kwargs['in_type'],
        )

        if kwargs['ip']:
            fields.update(ip=kwargs['ip'])
        if kwargs['fee']:
            fields.update(fee=kwargs['fee'])

        if kwargs['order_type'] == PayTypeEnum.DEPOSIT:
            order_cls = OrderDetailDeposit
        else:
            order_cls = OrderDetailWithdraw

            if kwargs['cost_type']:
                fields.update(cost_type=kwargs['cost_type'])

        return order_cls.add_model(fields, merchant=kwargs['merchant'], date=kwargs['create_time']), fields

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
    def create_order_event(
            cls,
            uid,
            amount,
            merchant: MerchantEnum,
            source: OrderSourceEnum,  # 订单来源
            order_type: PayTypeEnum,  # 订单类型
            in_type: InterfaceTypeEnum,  # 商户接入类型
            pay_method: PayMethodEnum = None,  # 支付方法
            create_time=None,
            bank_id=None,  # 用户提现银行卡ID
            ref_id=None,  # 票据ID
            op_account=None,  # 后台管理员账号，后台人工修改数据时必填
            comment=None,  # 管理后台修改备注，后台人工修改数据时必填
            mch_tx_id=None,  # 商户交易ID，当in_type为API时必填，其它时候选填
            channel_id: int = None,  # 通道费率ID，ABSChannelConfig 表中的主键ID，充值必填，提款不填
            mch_fee_id: int = None,  # 商户费率配置ID，MerchantFeeConfig 表的主键ID，充值必填，提款不填
            ip=None,
            fee=None,  # 提现订单，创建的时候就扣了手续费
            notify_url=None,
            result_url=None,
            extra=None,
            bank_info=None,  # 银行卡信息，用于API商户
            cost_type=None,
            commit=True,  # 是否立即提交事务
    ):
        if source == OrderSourceEnum.MANUALLY and not (op_account and comment):
            raise RuntimeError("人工修改订单必填管理员账号和备注")

        if in_type == InterfaceTypeEnum.API and not mch_tx_id:
            raise RuntimeError("开放API必须提供商户交易ID")

        if order_type == PayTypeEnum.DEPOSIT and not (channel_id and mch_fee_id):
            raise RuntimeError("充值必须填写channel_id/mch_fee_id/bank_id")

        if order_type == PayTypeEnum.WITHDRAW:
            if not (fee and mch_fee_id):
                raise RuntimeError("提现必须填写 fee/mch_fee_id")
            if not (bank_info or bank_id):
                raise RuntimeError("提现必须填写 bank_info 或 bank_id")

        create_time = create_time or DateTimeKit.get_cur_datetime()
        order_id = GlobalOrderId.generate_order_id(uid, order_type, create_time, merchant)
        sys_tx_id = OrderUtils.generate_sys_tx_id(order_id)

        if not mch_tx_id:
            mch_tx_id = OrderUtils.generate_mch_tx_id(order_id)

        params = copy.deepcopy(locals())
        params.pop('cls')

        if not ref_id:
            ref_id = OrderConstraint.apply_ref_id(order_id, order_type, OrderStateEnum.INIT)
            if not ref_id:
                return None, ''
            params['ref_id'] = ref_id

        try:
            # 订单模型
            rst, fields = cls.__create_order(**params)
            if rst['code'] != 0:
                OrderConstraint.revoke_order_state(order_id, OrderStateEnum.INIT)
                current_app.logger.error('failed to create order model, rst: %s, params: %s', rst, params)
                return None, ref_id

            models = list(rst['model'].values())
            order = rst['model']['hot']

            # 订单详情
            rst, fields = cls.__create_order_detail(**params)
            if rst['code'] != 0:
                OrderConstraint.revoke_order_state(order_id, OrderStateEnum.INIT)
                current_app.logger.error('failed to create order detail model, rst: %s, params: %s', rst, params)
                return None, ref_id

            models.extend(rst['model'].values())
            order_detail = rst['model']['hot']

            # 订单修改事件
            rst = cls.__create_event(**params)
            order_event = rst['model']
            order_event.data_after = [order.get_after_fields(), order_detail.get_after_fields()]
            models.append(order_event)

            # 提交事务
            assert len(models) == 5
            ModelOpMix.commit_models(models=models, commit=commit)

        except IntegrityError as e:
            OrderConstraint.revoke_order_state(order_id, OrderStateEnum.INIT)
            # sqlalchemy.exc.IntegrityError: (pymysql.err.IntegrityError) (1062, "Duplicate entry '4155' for key 'mch_tx_id'")
            msg = str(e)
            if 'Duplicate' in msg and 'mch_tx_id' in msg:
                # 订单号重复时不能重置订单状态
                msg = "商户订单号重复"
            current_app.logger.error(str(msg), exc_info=True)
            raise Exception(msg)

        except Exception as e:
            # 任何非期望的异常都要回滚状态
            OrderConstraint.revoke_order_state(order_id, OrderStateEnum.INIT)
            current_app.logger.error(str(e), exc_info=True)
            raise e

        return order, ref_id
