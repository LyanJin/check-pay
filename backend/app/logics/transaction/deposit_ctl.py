"""
充值流程
"""
import copy
import traceback

import requests
from flask import current_app

from app.enums.trade import PayTypeEnum, OrderSourceEnum, InterfaceTypeEnum, OrderStateEnum, BalanceTypeEnum, \
    BalanceAdjustTypeEnum, DeliverStateEnum
from app.extensions import db
from app.libs.error_code import InvalidDepositChannelError, ChannelNoValidityPeriodError, \
    DepositOrderAmountInvalidError, PreOrderCreateError, MerchantConfigDepositError
from app.libs.order_kit import OrderUtils
from app.logics.channel.chanel_cache import ChannelLimitCacheCtl
from app.logics.channel.channel_list import ChannelListHelper
from app.logics.gateway.sign_check import GatewaySign
from app.logics.order.create_ctl import OrderCreateCtl
from app.logics.order.order_fee import OrderFeeHelper
from app.logics.order.settle_helper import SettleHelper
from app.logics.order.update_ctl import OrderUpdateCtl
from app.models.balance import UserBalanceEvent
from app.models.channel import ChannelConfig
from app.models.merchant import MerchantFeeConfig, MerchantBalanceEvent
from app.models.order.order import OrderDeposit
from app.models.order.order_blobal import GlobalOrderId
from config import EnvironEnum


class DepositTransactionCtl:

    @classmethod
    def get_order_by_order_id(cls, order_id):
        """
        根据order id查询订单
        :param order_id:
        :return:
        """
        g_order_id = GlobalOrderId.query_global_id(order_id)
        if not g_order_id:
            msg = '无法从 GlobalOrderId 查到订单，order_id: %s' % order_id
            current_app.config['SENTRY_DSN'] and current_app.logger.fatal('msg: %s', msg)
            return None

        order = OrderDeposit.query_by_order_id(merchant=g_order_id.merchant, order_id=order_id)
        if not order:
            msg = '无法从 OrderDeposit 查到订单，order_id: %s' % order_id
            current_app.config['SENTRY_DSN'] and current_app.logger.fatal('msg: %s', msg)
            return None

        return order

    @classmethod
    def get_order(cls, tx_id):
        """
        根据交易ID查询订单
        :param tx_id:
        :return:
        """
        order_id = OrderUtils.parse_tx_id(tx_id)
        return cls.get_order_by_order_id(order_id)

    @classmethod
    def order_create(cls, user, amount, channel_enum, client_ip, source: OrderSourceEnum, in_type: InterfaceTypeEnum,
                     notify_url=None, result_url=None, mch_tx_id=None, extra=None):
        """
        申请创建订单
        :return:
        """
        merchant = user.merchant

        # 找出最新版本的商户费率配置
        channel_config = ChannelConfig.query_latest_one(query_fields=dict(channel_enum=channel_enum))
        if not channel_config:
            current_app.logger.error('no channel config found, channel_enum: %s', channel_enum.desc)
            return None, InvalidDepositChannelError()

        if channel_config.is_in_maintain_time():
            current_app.logger.error('channel in maintain, channel_enum: %s', channel_enum.desc)
            return None, ChannelNoValidityPeriodError(message="通道(%s)维护中" % channel_enum.desc)

        if not channel_config.is_in_trade_time():
            current_app.logger.error('channel not in trade time, channel_enum: %s', channel_enum.desc)
            return None, ChannelNoValidityPeriodError(message="当前时间不在通道(%s)交易时间内" % channel_enum.desc)

        if channel_config.is_amount_per_limit(amount):
            current_app.logger.error('per amount limit, channel_enum: %s, amount: %s', channel_enum.desc, amount)
            return None, DepositOrderAmountInvalidError(
                message="%s，通道(%s)" % (DepositOrderAmountInvalidError.message, channel_enum.desc))

        if channel_enum.is_fixed_amount_channel() and not channel_enum.is_amount_in_fixed_list(amount):
            current_app.logger.error('invalid amount, channel: %s, input amount: %s, fixed amounts: %s',
                                     channel_enum.desc, amount, channel_enum.get_fixed_amounts())
            return DepositOrderAmountInvalidError(message="固额支付类型额度匹配失败")

        if not channel_config.state.is_available(user.is_test_user):
            current_app.logger.error('channel state not available, channel_enum: %s, uid: %s, merchant: %s',
                                     channel_enum.desc, user.uid, merchant.name)
            return None, ChannelNoValidityPeriodError(
                message="通道(%s)状态：%s" % (channel_enum.desc, channel_config.state.desc))

        # 找出最新版本的商户费率配置
        merchant_fee = MerchantFeeConfig.query_latest_one(query_fields=dict(
            merchant=merchant,
            payment_way=PayTypeEnum.DEPOSIT,
            payment_method=channel_enum.conf.payment_method
        ))

        if not merchant_fee:
            current_app.logger.error('no merchant fee config for channel, channel_enum: %s, uid: %s, merchant: %s',
                                     channel_enum.desc, user.uid, merchant.name)
            return None, MerchantConfigDepositError()

        kwargs = dict(
            uid=user.uid,
            merchant=merchant,
            amount=amount,
            channel_id=channel_config.channel_id,
            mch_fee_id=merchant_fee.config_id,
            order_type=PayTypeEnum.DEPOSIT,
            source=source,
            in_type=in_type,
            ip=client_ip,
            pay_method=channel_enum.conf.payment_method,
            notify_url=notify_url,
            result_url=result_url,
            mch_tx_id=mch_tx_id,
            extra=extra,
        )

        try:
            order, _ = OrderCreateCtl.create_order_event(**kwargs)
        except Exception as e:
            return None, PreOrderCreateError(message=str(e))

        if not order:
            return None, PreOrderCreateError()

        return order, None

    @classmethod
    def order_update(cls, order, channel_tx_id):
        """
        更新订单
        :param order:
        :param channel_tx_id:
        :return:
        """
        params = copy.deepcopy(locals())
        params.pop('order')

        order, ref_id = OrderUpdateCtl.update_order_event(
            order_id=order.order_id,
            uid=order.uid,
            merchant=order.merchant,
            channel_tx_id=channel_tx_id,
        )
        if not order:
            current_app.logger.error('update order failed, sys_tx_id: %s, params: %s', order.sys_tx_id, params)
            return None, PreOrderCreateError()
        return order, None

    @classmethod
    def order_create_fail(cls, order):
        """
        订单创建失败处理
        :return:
        """
        order, ref_id = OrderUpdateCtl.update_order_event(
            order_id=order.order_id,
            uid=order.uid,
            merchant=order.merchant,
            state=OrderStateEnum.FAIL,
        )
        if not order:
            current_app.logger.error('update order failed, sys_tx_id: %s', order.sys_tx_id)
            return False
        return True

    @classmethod
    def failed_order_process(cls, order, tx_amount, channel_tx_id):
        """
        处理充值失败的订单
        :param order:
        :param tx_amount: 实际支付金额
        :param channel_tx_id: 通道订单号
        :return:
        """
        params = copy.deepcopy(locals())
        params.pop('cls')
        params.pop('order')
        params['tx_id'] = order.sys_tx_id

        order, _ = OrderUpdateCtl.update_order_event(
            order.order_id,
            uid=order.uid,
            merchant=order.merchant,
            state=OrderStateEnum.FAIL,
            channel_tx_id=channel_tx_id,
            tx_amount=tx_amount,
        )
        if not order:
            msg = '充值订单状态更新失败, params: %s' % params
            current_app.config['SENTRY_DSN'] and current_app.logger.fatal('msg: %s', msg)
            return False

        cls.do_notify(order)

        return True

    @classmethod
    def success_order_process(cls, order, tx_amount, channel_tx_id=None, comment: str = '', op_account=None, commit=True):
        """
        处理充值成功的订单
        :param order:
        :param tx_amount: 实际支付金额
        :param channel_tx_id: 通道订单号
        :param comment: 备注
        :param op_account: 备注
        :param commit: 是否立即提交事务
        :return:
        """
        params = copy.deepcopy(locals())
        params.pop('cls')
        params.pop('order')
        params['tx_id'] = order.sys_tx_id

        rst = dict(
            code=0,
            msg='',
        )

        # 计算一笔订单的各种费用
        channel_config = ChannelConfig.query_by_channel_id(order.channel_id)
        merchant_config = MerchantFeeConfig.query_by_config_id(order.mch_fee_id)
        order_fee = OrderFeeHelper.calc_order_fee(order, tx_amount, channel_config, merchant_config)

        try:
            with db.auto_commit(commit):
                order, ref_id = OrderUpdateCtl.update_order_event(
                    order.order_id,
                    uid=order.uid,
                    merchant=order.merchant,
                    state=OrderStateEnum.SUCCESS,
                    channel_tx_id=channel_tx_id,
                    tx_amount=tx_amount,
                    offer=order_fee['offer'],  # 优惠金额
                    fee=order_fee['merchant_fee'],  # 手续费
                    cost=order_fee['channel_cost'],  # 成本金额
                    profit=order_fee['profit'],  # 利润（收入）金额
                    commit=False,
                    pay_method=channel_config.channel_enum.conf['payment_method'],
                    comment=comment,
                    op_account=op_account,
                )
                if not order:
                    msg = '订单更新失败, params: %s' % params
                    raise RuntimeError(msg)

                # 给用户充值
                code, msg = UserBalanceEvent.update_user_balance(
                    uid=order.uid,
                    merchant=order.merchant,
                    ref_id=ref_id,
                    source=order.source,
                    order_type=order.order_type,
                    bl_type=BalanceTypeEnum.AVAILABLE,
                    value=order.amount,
                    ad_type=BalanceAdjustTypeEnum.PLUS,
                    comment=comment,
                    tx_id=order.sys_tx_id,
                    commit=False,
                )
                if code != 0:
                    raise RuntimeError(msg)

                # 根据结算类型获取商户余额变更类型
                balance_type = SettleHelper.get_balance_type_by_settle(channel_config.settlement_type)

                # 更新商户余额，加用户充值金额
                code, msg = MerchantBalanceEvent.update_balance(
                    merchant=order.merchant,
                    ref_id=ref_id,
                    source=order.source,
                    order_type=order.order_type,
                    bl_type=balance_type,
                    value=order.amount,
                    ad_type=BalanceAdjustTypeEnum.PLUS,
                    tx_id=order.sys_tx_id,
                    comment=comment,
                    commit=False,
                )
                if code != 0:
                    raise RuntimeError(msg)

                # 更新商户余额，扣手续费
                ref_id = OrderUtils.gen_unique_ref_id()
                code, msg = MerchantBalanceEvent.update_balance(
                    merchant=order.merchant,
                    ref_id=ref_id,
                    source=order.source,
                    order_type=PayTypeEnum.FEE,
                    bl_type=balance_type,
                    value=order_fee['merchant_fee'],
                    ad_type=BalanceAdjustTypeEnum.MINUS,
                    tx_id=order.sys_tx_id,
                    comment=comment,
                    commit=False,
                )
                if code != 0:
                    raise RuntimeError(msg)

        except RuntimeError as e:
            current_app.logger.error('An error occurred.', exc_info=True)
            return False

        # 累计当天通道充值额度
        ChannelLimitCacheCtl.add_day_amount(channel_config.channel_enum, order.amount)

        cls.do_notify(order)

        return True

    @classmethod
    def do_notify(cls, order, op_account=None, comment=None):
        """
        网关回调通知
        :return:
        """
        rst = dict(
            msg=None
        )
        if not order.notify_url:
            # 不需要通知
            rst['msg'] = "没有通知URL，不需要发送通知"
            return rst

        if order.state not in OrderStateEnum.get_final_states() and \
                EnvironEnum.is_production(current_app.config['FLASK_ENV']):
            rst['msg'] = "订单不是成功/失败状态，还没有完成，不能通知商户"
            return rst

        data = dict(
            merchant_id=order.merchant.value,
            amount=str(order.amount),
            tx_amount=str(order.tx_amount),
            mch_tx_id=order.mch_tx_id,
            sys_tx_id=order.sys_tx_id,
            state=order.state.name,
        )

        data['sign'] = GatewaySign(order.merchant).generate_sign(data)
        data['extra'] = order.extra

        try:
            current_app.logger.info('do_notify: %s, data: %s', order.notify_url, data)
            rsp = requests.post(order.notify_url, json=data)
            current_app.logger.info('do_notify: %s, status code: %s, data: %s', order.notify_url, rsp.status_code,
                                    rsp.text)
        except:
            current_app.logger.fatal(traceback.format_exc())
            current_app.logger.error('do_notify, url: %s, request data: %s', order.notify_url, data)
            rst['msg'] = "通知失败，HTTP网络异常"
            return rst

        if rsp.status_code != 200:
            current_app.logger.error('do_notify, url: %s, request data: %s, response data: %s', order.notify_url, data,
                                     rsp.text)
            rst['msg'] = "通知失败，HTTP status_code非200：%s" % rsp.status_code
            return rst

        try:
            json_data = rsp.json()
        except:
            current_app.logger.error('do_notify, url: %s, request data: %s, response data: %s', order.notify_url, data,
                                     rsp.text)
            current_app.logger.fatal(traceback.format_exc())
            rst['msg'] = "通知失败，无法解析json数据"
            return rst

        if json_data['error_code'] != 200:
            rst['msg'] = "通知失败，error_code非200：%s" % json_data['error_code']
            current_app.logger.error('do_notify, url: %s, request data: %s, response data: %s', order.notify_url, data,
                                     json_data)
            return rst

        # 更新订单通知完成
        if order.deliver != DeliverStateEnum.DONE:
            order, ref_id = OrderUpdateCtl.update_order_event(
                order_id=order.order_id,
                uid=order.uid,
                merchant=order.merchant,
                deliver=DeliverStateEnum.DONE,
                op_account=op_account,
                comment=comment,
            )
            if not order:
                rst['msg'] = '订单更新失败, 请研发检查错误日志， sys_tx_id: %s' % (order.sys_tx_id,)
                current_app.logger.fatal(rst['msg'])
                return rst

        rst['msg'] = "通知成功"
        return rst
