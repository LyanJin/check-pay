"""
提款代付流程
"""
import copy
import importlib
import traceback

import requests
from flask import current_app

from app.enums.trade import PayTypeEnum, OrderSourceEnum, InterfaceTypeEnum, BalanceTypeEnum, BalanceAdjustTypeEnum, \
    OrderStateEnum, DeliverTypeEnum, DeliverStateEnum, CostTypeEnum
from app.extensions import db
from app.libs.api_exception import APIException
from app.libs.datetime_kit import DateTimeKit
from app.libs.error_code import WithdrawOrderAmountInvalidError, AccountBalanceInsufficientError, \
    WithdrawBankNoExistError, WithdrawOrderCreateError, DepositCallbackUserBalanceError, NoSuchWithdrawOrderError, \
    DoNotAllowedOrderError, AllowedOrderError, NotAllocOrderError, InvalidChannelError, \
    FailedLaunchWithdrawError, WithdrawUpdateDealingError, ResponseSuccess, WithdrawOrderStateChangeError, \
    OrderInfoMissingError, BankOrderStateError, NosuchOrderDetailDataError, WithdrawFeeEmptyError
from app.libs.order_kit import OrderUtils
from app.logics.channel.chanel_cache import ChannelLimitCacheCtl
from app.logics.channel.channel_list import ChannelListHelper
from app.logics.gateway.sign_check import GatewaySign
from app.logics.order.create_ctl import OrderCreateCtl
from app.logics.order.fee_calculator import FeeCalculator
from app.logics.order.update_ctl import OrderUpdateCtl
from app.models.balance import UserBalance, UserBalanceEvent
from app.models.bankcard import BankCard
from app.models.channel import ProxyChannelConfig, ChannelConfig
from app.models.merchant import MerchantFeeConfig, MerchantInfo, MerchantBalanceEvent
from app.models.order.order import OrderWithdraw
from app.models.order.order_blobal import OrderConstraint, GlobalOrderId
from app.models.order.order_detail import OrderDetailWithdraw
from config import EnvironEnum


class WithdrawTransactionCtl:

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

        order = OrderWithdraw.query_by_order_id(merchant=g_order_id.merchant, order_id=order_id)
        if not order:
            msg = '无法从 OrderWithdraw 查到订单，order_id: %s' % order_id
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
    def order_create(cls, user, amount, client_ip, user_bank_id=None, bank_info=None, notify_url=None, mch_tx_id=None,
                     extra=None):
        """
        申请创建订单
        :return:
        """
        params = copy.deepcopy(locals())
        params.pop('cls')

        order = None

        if not bank_info:
            card_entry = BankCard.query_bankcard_by_id(card_id=user_bank_id)
            if not card_entry:
                msg = '%s, params: %s' % (WithdrawBankNoExistError.message, params)
                current_app.logger.error(msg)
                return order, WithdrawBankNoExistError()

        # 判断 金额是否在有效范围 获取代付系统当前最高最低交易金额
        # limit_min, limit_max = ChannelLimitCacheCtl(PayTypeEnum.WITHDRAW).get_channel_limit()
        # if amount < limit_min or amount > limit_max:
        if ChannelListHelper.is_amount_out_of_range(amount=amount, merchant=user.merchant,
                                                    payment_way=PayTypeEnum.WITHDRAW, client_ip=client_ip):
            msg = '%s, params: %s' % (WithdrawOrderAmountInvalidError.message, params)
            current_app.logger.error(msg)
            return order, WithdrawOrderAmountInvalidError()

        # 商户配置信息
        merchant_config = MerchantFeeConfig.query_latest_one(query_fields=dict(
            merchant=user.merchant,
            payment_way=PayTypeEnum.WITHDRAW,
        ))

        # 手续费计算
        fee_value = FeeCalculator.calc_fee(amount, merchant_config.fee_type, merchant_config.value)
        user_fee = merchant_fee = 0
        if merchant_config.cost_type == CostTypeEnum.MERCHANT:
            merchant_fee = fee_value
        elif merchant_config.cost_type == CostTypeEnum.USER:
            user_fee = fee_value
            # 用户实际到账金额要减去手续费
            amount -= user_fee

        # 用户余额判断
        if user.uid:
            user_balance = UserBalance.query_balance(uid=user.uid, merchant=user.merchant).first()
            if user_balance.real_balance < amount + user_fee:
                msg = '%s, params: %s' % ("用户余额不足", params)
                current_app.logger.error(msg)
                return order, AccountBalanceInsufficientError(message="用户余额不足")

        # 判断商户余额是否充足
        merchant_balance = MerchantInfo.query_merchant(m_name=user.merchant)
        if merchant_balance.balance_available <= amount + merchant_fee:
            msg = '%s, params: %s' % ("商户余额不足", params)
            current_app.logger.error(msg)
            return order, AccountBalanceInsufficientError(message="商户余额不足")

        # 订单来源
        source = OrderSourceEnum.TESTING if user.is_test_user else OrderSourceEnum.ONLINE

        try:
            # 创建提现订单/扣商户余额/扣用户余额，在同一个事务里面
            with db.auto_commit():
                order, ref_id = OrderCreateCtl.create_order_event(uid=user.uid,
                                                                  amount=amount,
                                                                  merchant=user.merchant,
                                                                  source=source,
                                                                  order_type=PayTypeEnum.WITHDRAW,
                                                                  in_type=InterfaceTypeEnum.CASHIER_H5,
                                                                  bank_id=user_bank_id,  # 提现时需要填入 银行卡信息
                                                                  mch_fee_id=merchant_config.config_id,
                                                                  mch_tx_id=mch_tx_id,
                                                                  ip=client_ip,
                                                                  fee=fee_value,
                                                                  cost_type=merchant_config.cost_type,
                                                                  notify_url=notify_url,
                                                                  bank_info=bank_info,
                                                                  extra=extra,
                                                                  commit=False,
                                                                  )

                if not order:
                    msg = '%s, params: %s' % (WithdrawOrderCreateError.message, params)
                    current_app.logger.error(msg)
                    raise WithdrawOrderCreateError()

                # 扣提现金额
                flag, msg = MerchantBalanceEvent.update_balance(merchant=user.merchant,
                                                                ref_id=ref_id,
                                                                source=source,
                                                                order_type=PayTypeEnum.WITHDRAW,
                                                                bl_type=BalanceTypeEnum.AVAILABLE,
                                                                value=amount,
                                                                ad_type=BalanceAdjustTypeEnum.MINUS,
                                                                tx_id=order.sys_tx_id,
                                                                commit=False,
                                                                )
                if flag < 0:
                    msg = '%s, params: %s' % ("扣商户余额失败, %s" % msg, params)
                    current_app.logger.error(msg)
                    raise DepositCallbackUserBalanceError(message="扣商户余额失败")

                if merchant_fee:
                    # 扣商户手续费
                    flag, msg = MerchantBalanceEvent.update_balance(merchant=user.merchant,
                                                                    ref_id=OrderUtils.gen_unique_ref_id(),
                                                                    source=source,
                                                                    order_type=PayTypeEnum.FEE,
                                                                    bl_type=BalanceTypeEnum.AVAILABLE,
                                                                    value=merchant_fee,
                                                                    ad_type=BalanceAdjustTypeEnum.MINUS,
                                                                    tx_id=order.sys_tx_id,
                                                                    commit=False,
                                                                    )
                    if flag < 0:
                        msg = '%s, params: %s' % ("扣商户手续费失败, %s" % msg, params)
                        current_app.logger.error(msg)
                        raise DepositCallbackUserBalanceError(message="扣商户手续费失败")

                if user_fee:
                    # 扣除用户手续费
                    flag, msg = UserBalanceEvent.update_user_balance(uid=user.uid,
                                                                     merchant=user.merchant,
                                                                     ref_id=OrderUtils.gen_unique_ref_id(),
                                                                     source=source,
                                                                     order_type=PayTypeEnum.FEE,
                                                                     bl_type=BalanceTypeEnum.AVAILABLE,
                                                                     value=user_fee,
                                                                     ad_type=BalanceAdjustTypeEnum.MINUS,
                                                                     tx_id=order.sys_tx_id,
                                                                     commit=False,
                                                                     )
                    if flag < 0:
                        msg = '%s, params: %s' % ("扣用户手续费失败, %s" % msg, params)
                        current_app.logger.error(msg)
                        raise DepositCallbackUserBalanceError(message="扣用户手续费失败")

                # 扣除用户余额
                flag, msg = UserBalanceEvent.update_user_balance(uid=user.uid,
                                                                 merchant=user.merchant,
                                                                 ref_id=ref_id,
                                                                 source=source,
                                                                 order_type=PayTypeEnum.WITHDRAW,
                                                                 bl_type=BalanceTypeEnum.AVAILABLE,
                                                                 value=amount,
                                                                 ad_type=BalanceAdjustTypeEnum.MINUS,
                                                                 tx_id=order.sys_tx_id,
                                                                 commit=False,
                                                                 )
                if flag < 0:
                    msg = '%s, params: %s' % ("扣用户余额失败, %s" % msg, params)
                    current_app.logger.error(msg)
                    raise DepositCallbackUserBalanceError(message="扣用户余额失败")

        except APIException as e:
            current_app.logger.error(traceback.format_exc())
            return order, e

        return order, None

    @classmethod
    def order_alloc(cls, admin_account, order_id, merchant):
        """
        认领分配订单
        :return:
        """
        params = copy.deepcopy(locals())
        params.pop('cls')

        order = OrderWithdraw.query_by_order_id(merchant, order_id)
        if not order:
            msg = '%s, params: %s' % (NoSuchWithdrawOrderError.message, params)
            current_app.logger.error(msg)
            return NoSuchWithdrawOrderError()

        if order.state != OrderStateEnum.INIT:
            msg = '%s, params: %s' % (DoNotAllowedOrderError.message, params)
            current_app.logger.error(msg)
            return DoNotAllowedOrderError()

        order, ref_id = OrderUpdateCtl.update_order_event(
            order.order_id,
            uid=order.uid,
            merchant=merchant,
            state=OrderStateEnum.ALLOC,
            op_account=admin_account,
            alloc_time=DateTimeKit.get_cur_datetime(),
        )

        if not order:
            msg = '%s, params: %s' % (AllowedOrderError.message, params)
            current_app.logger.error(msg)
            return AllowedOrderError()

        return ResponseSuccess()

    @classmethod
    def order_deal(cls, admin_account, order_id, merchant, channel_id, test=False):
        """

        :param admin_account:
        :param order_id:
        :param merchant:
        :param channel_id:
        :param test: 单元测试填写
        :return:
        """
        params = copy.deepcopy(locals())
        params.pop('cls')

        if EnvironEnum.is_production(current_app.config['FLASK_ENV']) and test:
            # 非调试环境不该填写 channel_tx_id，应该发送请求到第三方去申请
            raise RuntimeError('invalid test param')

        order = OrderWithdraw.query_by_order_id(merchant, order_id)
        if not order:
            msg = '%s, params: %s' % (NoSuchWithdrawOrderError.message, params)
            current_app.logger.error(msg)
            return NoSuchWithdrawOrderError()

        if order.state != OrderStateEnum.ALLOC:
            msg = '%s, params: %s, state: %s, tx_id: %s' % (NotAllocOrderError.message, params, order.state.desc,
                                                            order.sys_tx_id)
            current_app.logger.error(msg)
            return NotAllocOrderError(message=NotAllocOrderError.message + ", 订单状态：" + order.state.desc)

        channel_config = ProxyChannelConfig.query_by_channel_id(channel_id)
        if not channel_config:
            msg = '%s, params: %s' % (InvalidChannelError.message, params)
            current_app.logger.error(msg)
            return InvalidChannelError()

        bank_card = order.get_bank_card()
        if not bank_card:
            msg = '%s, params: %s' % (WithdrawBankNoExistError.message, params)
            current_app.logger.error(msg)
            return WithdrawBankNoExistError()

        # 开始更新订单，根据通道计算费率和成本
        # 通道收取的手续费
        channel_cost = FeeCalculator.calc_cost(order.amount, channel_config.fee_type, channel_config.fee)
        tx_amount = order.amount

        channel_enum = channel_config.channel_enum
        if channel_enum.plus_fee_for_withdraw():
            # 特殊通道，要发起金额要加上手续费，通道测扣除手续费才是实际到账金额
            # 实际提款金额=发起金额+通道手续费
            tx_amount += channel_cost

        # 发起支付
        launch_pay = channel_enum.get_launch_pay_func(PayTypeEnum.WITHDRAW)

        if not test:
            # 第三方返回由第三方生成交易ID：channel_tx_id
            rst = launch_pay(dict(
                order_id=order.order_id,
                tx_id=order.sys_tx_id,
                amount=tx_amount,
                channel_cost=channel_cost,
                bank_code=bank_card.bank_code,
                bank_name=bank_card.bank_name,
                bank_account=bank_card.account_name,
                bank_number=bank_card.card_no,
                bank_address=bank_card.bank_address,
                bank_branch=bank_card.branch,
                province=bank_card.province,
                city=bank_card.city
            ))

            current_app.logger.info('withdraw launch_pay, params: %s, rst: %s', params, rst)

            if rst['code'] != 0:
                # 不要改变订单状态，让客服去选择其它通道重试
                # cls.order_fail(order, client_ip)
                current_app.logger.error('%s, %s, params: %s' % (FailedLaunchWithdrawError.message, rst['msg'], params))
                return FailedLaunchWithdrawError(message=rst['msg'])

        # 发起成功后更新状态为处理中
        order, _ = OrderUpdateCtl.update_order_event(
            order.order_id,
            uid=order.uid,
            merchant=merchant,
            state=OrderStateEnum.DEALING,
            channel_id=channel_id,
            cost=channel_cost,
            deal_time=DateTimeKit.get_cur_datetime(),
            op_account=admin_account,
        )
        if not order:
            msg = '%s, params: %s' % (WithdrawUpdateDealingError.message, params)
            current_app.logger.error(msg)
            return WithdrawUpdateDealingError()

        return ResponseSuccess()

    @classmethod
    def order_success(cls, order, tx_amount):
        """
        订单成功处理
        :return:
        """
        params = copy.deepcopy(locals())
        params.pop('order')
        params.pop('cls')
        params['tx_id'] = order.sys_tx_id

        rst = dict(
            code=0,
            msg='',
        )

        # 计算利润
        order_detail = OrderDetailWithdraw.query_by_order_id(order.merchant, order.order_id, order.create_time)
        profit = FeeCalculator.calc_profit(order_detail.fee, order_detail.cost)

        order, ref_id = OrderUpdateCtl.update_order_event(
            order.order_id,
            uid=order.uid,
            merchant=order.merchant,
            state=OrderStateEnum.SUCCESS,
            tx_amount=tx_amount,
            profit=profit,
        )
        if not order:
            current_app.logger.error('提现订单修改成功状态失败, ref_id: %s, sys_tx_id: %s', ref_id, params)
            return False

        # 累计当天通道充值额度
        channel_config = ProxyChannelConfig.query_by_channel_id(order.channel_id)
        ChannelLimitCacheCtl.add_day_amount(channel_config.channel_enum, order.amount)

        cls.do_notify(order=order)

        return True

    @classmethod
    def order_fail(cls, order):
        """
        订单失败处理
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

        # 手续费存在订单详情里面
        order_detail = OrderDetailWithdraw.query_by_order_id(order.merchant, order.order_id, order.create_time)
        merchant_config = MerchantFeeConfig.query_by_config_id(order.mch_fee_id)

        try:
            # 创建提现订单/扣商户余额/扣用户余额，在同一个事务里面
            with db.auto_commit():
                order, ref_id = OrderUpdateCtl.update_order_event(
                    order.order_id,
                    uid=order.uid,
                    merchant=order.merchant,
                    state=OrderStateEnum.FAIL,
                    commit=False,
                )
                if not order:
                    raise RuntimeError('提现订单修改失败状态失败, params: %s' % params)

                # 给商户退回提现订单的发起金额
                flag, msg = MerchantBalanceEvent.update_balance(merchant=order.merchant,
                                                                ref_id=ref_id,
                                                                source=order.source,
                                                                order_type=PayTypeEnum.REFUND,
                                                                bl_type=BalanceTypeEnum.AVAILABLE,
                                                                # 订单发起金额
                                                                value=order.amount,
                                                                ad_type=BalanceAdjustTypeEnum.PLUS,
                                                                tx_id=order.sys_tx_id,
                                                                commit=False,
                                                                )
                # print('update_balance', flag, msg)
                if flag < 0:
                    raise RuntimeError(msg + ", params: %s" % params)

                if merchant_config.cost_type == CostTypeEnum.MERCHANT:
                    # 给商户退回提手续费
                    flag, msg = MerchantBalanceEvent.update_balance(merchant=order.merchant,
                                                                    ref_id=OrderUtils.gen_unique_ref_id(),
                                                                    tx_id=order.sys_tx_id,
                                                                    source=order.source,
                                                                    order_type=PayTypeEnum.FEE,
                                                                    bl_type=BalanceTypeEnum.AVAILABLE,
                                                                    # 收取商户的手续费
                                                                    value=order_detail.fee,
                                                                    ad_type=BalanceAdjustTypeEnum.PLUS,
                                                                    commit=False,
                                                                    )
                    # print('update_balance', flag, msg)
                    if flag < 0:
                        raise RuntimeError(msg + ", params: %s" % params)

                refund_fee = order.amount
                if merchant_config.cost_type == CostTypeEnum.USER:
                    # 给用户退回手续费
                    refund_fee += order_detail.fee

                # 给用户退回发起金额
                flag, msg = UserBalanceEvent.update_user_balance(uid=order.uid,
                                                                 merchant=order.merchant,
                                                                 ref_id=ref_id,
                                                                 source=order.source,
                                                                 order_type=PayTypeEnum.REFUND,
                                                                 bl_type=BalanceTypeEnum.AVAILABLE,
                                                                 # 订单发起金额
                                                                 value=refund_fee,
                                                                 ad_type=BalanceAdjustTypeEnum.PLUS,
                                                                 tx_id=order.sys_tx_id,
                                                                 commit=False,
                                                                 )
                # print('update_user_balance', flag, msg)
                if flag < 0:
                    raise RuntimeError(msg + ", params: %s" % params)

        except APIException as e:
            current_app.logger.error(traceback.format_exc())
            return False

        cls.do_notify(order=order)

        return True

    @classmethod
    def manually_withdraw(cls, admin_user, merchant, order_id):
        """
        人工出款
        :return:
        """
        # 查询 提现订单表 获取提现金额， 提现用户指定行
        withdraw_entry = OrderWithdraw.query_by_order_id(merchant=merchant, order_id=order_id)
        if not withdraw_entry:
            return OrderInfoMissingError()

        if withdraw_entry.state != OrderStateEnum.ALLOC:
            return BankOrderStateError()

        # 更新订单状态
        order, ref_id = OrderUpdateCtl.update_order_event(
            withdraw_entry.order_id,
            uid=int(withdraw_entry.uid),
            merchant=merchant,
            state=OrderStateEnum.DEALING,
            tx_amount=withdraw_entry.amount,
            deliver_type=DeliverTypeEnum.MANUALLY,
            deal_time=DateTimeKit.get_cur_datetime(),
            op_account=admin_user.account,
            mch_fee_id=withdraw_entry.mch_fee_id,
            commit=True
        )
        if not order:
            return WithdrawOrderStateChangeError()

        return ResponseSuccess()

    @classmethod
    def manually_withdraw_success(cls, admin_user, merchant, order_id, channel_cost, comment):
        """
        完成人工出款
        :return:
        """

        withdraw_entry = OrderWithdraw.query_by_order_id(merchant=merchant, order_id=order_id)
        if not withdraw_entry:
            return OrderInfoMissingError()

        if withdraw_entry.state != OrderStateEnum.DEALING:
            return BankOrderStateError()

        detail = OrderDetailWithdraw.query_by_order_id(order_id=withdraw_entry.order_id,
                                                       merchant=merchant,
                                                       create_time=withdraw_entry.create_time)
        if not detail:
            return NosuchOrderDetailDataError()

        if detail.fee == 0:
            return WithdrawFeeEmptyError()

        # 更新订单状态

        profit = FeeCalculator.calc_profit(detail.fee, channel_cost)

        order, ref_id = OrderUpdateCtl.update_order_event(
            withdraw_entry.order_id,
            uid=int(withdraw_entry.uid),
            merchant=merchant,
            tx_amount=withdraw_entry.amount,
            state=OrderStateEnum.SUCCESS,
            deliver_type=DeliverTypeEnum.MANUALLY,
            op_account=admin_user.account,
            comment=comment,
            cost=channel_cost,
            profit=profit,
            mch_fee_id=withdraw_entry.mch_fee_id,
            commit=True
        )
        if not order:
            return WithdrawOrderStateChangeError()

        cls.do_notify(
            order=order,
            op_account=admin_user.account,
            comment=comment,
        )

        return ResponseSuccess()

    @classmethod
    def manually_withdraw_failed(cls, admin_user, merchant, order_id):
        """
        手动更新提款状态为失败
        退款/审核拒绝
                流程：
            1. 获取创建订单时 扣除 用户及商户的费用
                获取订单 withdrawOrderDetail 数据， 获取 手续费 提现金额
            2. 给用户和商户新增费用
                更新 UserBalance 表
                更新 MerchantBalance表
            3. 修改订单状态
                更新 OrderUpdateCtl
        :param admin_user:
        :param merchant:
        :param order_id:
        :return:
        """
        # 查询该笔订单是否存在
        withdraw_entry = OrderWithdraw.query_by_order_id(merchant=merchant, order_id=order_id)
        # 判断是否存在
        if not withdraw_entry:
            return OrderInfoMissingError()

        # 判断订单状态是否为 已认领 或 提现成功
        if withdraw_entry.state not in [OrderStateEnum.ALLOC, OrderStateEnum.SUCCESS]:
            return BankOrderStateError()

        detail = OrderDetailWithdraw.query_by_order_id(order_id=withdraw_entry.order_id,
                                                       merchant=merchant,
                                                       create_time=withdraw_entry.create_time)
        if not detail:
            return NosuchOrderDetailDataError()

        # 提现订单 手续费 提现订单费用
        fee = detail.fee
        amount = detail.amount

        comment = "出款失败" if withdraw_entry.state == OrderStateEnum.SUCCESS else "系统拒绝"
        order_type = PayTypeEnum.REFUND if withdraw_entry.state == OrderStateEnum.SUCCESS else PayTypeEnum.MANUALLY

        merchant_config = MerchantFeeConfig.query_by_config_id(withdraw_entry.mch_fee_id)

        # 更新订单状态
        try:
            with db.auto_commit():

                order, ref_id = OrderUpdateCtl.update_order_event(
                    withdraw_entry.order_id,
                    uid=int(withdraw_entry.uid),
                    merchant=merchant,
                    state=OrderStateEnum.FAIL,
                    tx_amount=withdraw_entry.amount,
                    deliver_type=DeliverTypeEnum.MANUALLY,
                    op_account=admin_user.account,
                    commit=False
                )

                if not order:
                    msg = WithdrawOrderStateChangeError.message
                    current_app.logger.error(msg)
                    raise WithdrawOrderStateChangeError()

                # 加提现金额
                flag, msg = MerchantBalanceEvent.update_balance(merchant=merchant,
                                                                ref_id=ref_id,
                                                                order_type=order_type,
                                                                bl_type=BalanceTypeEnum.AVAILABLE,
                                                                value=amount,
                                                                ad_type=BalanceAdjustTypeEnum.PLUS,
                                                                tx_id=order.sys_tx_id,
                                                                source=OrderSourceEnum.MANUALLY,
                                                                comment=comment,
                                                                commit=False,
                                                                )
                if flag < 0:
                    msg = '%s' % ("提现退回增加商户余额失败, %s" % msg)
                    current_app.logger.error(msg)
                    raise DepositCallbackUserBalanceError()

                if merchant_config.cost_type == CostTypeEnum.MERCHANT:
                    # 给商户加手续费
                    flag, msg = MerchantBalanceEvent.update_balance(merchant=merchant,
                                                                    ref_id=OrderUtils.gen_unique_ref_id(),
                                                                    order_type=PayTypeEnum.FEE,
                                                                    bl_type=BalanceTypeEnum.AVAILABLE,
                                                                    value=fee,
                                                                    ad_type=BalanceAdjustTypeEnum.PLUS,
                                                                    tx_id=order.sys_tx_id,
                                                                    commit=False,
                                                                    comment=comment,
                                                                    source=OrderSourceEnum.MANUALLY
                                                                    )
                    if flag < 0:
                        msg = '%s' % ("提现退款增加商户手续费失败, %s" % msg)
                        current_app.logger.error(msg)
                        raise DepositCallbackUserBalanceError()

                refund_fee = amount
                if merchant_config.cost_type == CostTypeEnum.USER:
                    # 给用户退回手续费
                    refund_fee += fee

                # 增加用户余额
                flag, msg = UserBalanceEvent.update_user_balance(uid=order.uid,
                                                                 merchant=merchant,
                                                                 ref_id=ref_id,
                                                                 order_type=order_type,
                                                                 bl_type=BalanceTypeEnum.AVAILABLE,
                                                                 value=refund_fee,
                                                                 ad_type=BalanceAdjustTypeEnum.PLUS,
                                                                 tx_id=order.sys_tx_id,
                                                                 commit=False,
                                                                 comment=comment,
                                                                 source=OrderSourceEnum.MANUALLY
                                                                 )
                if flag < 0:
                    msg = '%s' % ("提现退款增加用户余额失败, %s" % msg)
                    current_app.logger.error(msg)
                    raise DepositCallbackUserBalanceError()

        except APIException as e:
            current_app.logger.error(traceback.format_exc())
            return e

        cls.do_notify(
            order=order,
            op_account=admin_user.account,
            comment=comment,
        )

        return ResponseSuccess()

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

        if order.state not in OrderStateEnum.get_final_states():
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
