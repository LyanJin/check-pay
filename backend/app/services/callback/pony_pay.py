from decimal import Decimal

from flask import current_app, request
from werkzeug.wrappers import BaseResponse

from app.forms.deposit_channel_notify_form import PonyPayForm, PonyPayWithdrawForm
from app.libs.doc_response import ResponseDoc
from app.libs.ip_kit import IpKit
from app.libs.order_kit import OrderUtils
from app.channel.ponypay.deposit.callback import CallbackPonypay
from app.channel.ponypay.withdraw.callback import WithdrawCallbackPonypay
from app.logics.transaction.deposit_ctl import DepositTransactionCtl
from app.logics.transaction.withdraw_ctl import WithdrawTransactionCtl
from app.models.channel import ChannelConfig
from config import EnvironEnum
from . import api
from flask_restplus import Resource

ns = api.namespace('callback', description='用户充值')


@ns.route('/ponypay/deposit')
@ResponseDoc.response(ns, api)
class PonypayDeposit(Resource):

    def get(self):
        """
        立马付，充值回调
        :return:
        """
        if not EnvironEnum.is_local_evn(current_app.config['FLASK_ENV']):
            # 无论如何都记录一条log
            current_app.logger.info('ponypay deposit callback, ip: %s, data: %s', IpKit.get_remote_ip(), request.args)

        form, error = PonyPayForm().request_validate()
        if error:
            current_app.logger.fatal('msg: %s, data: %s', error.message, request.args)
            return BaseResponse(error.message)

        # 交易订单id
        tx_id = form.orderid.data
        # 充值通道 订单id
        channel_tx_id = form.porder.data
        # 实际支付金额
        tx_amount = Decimal(form.money.data)
        # 订单状态： 成功/失败
        status = form.status.data
        # 客户端IP
        client_ip = form.client_ip.data

        # IP白名单校验
        if not CallbackPonypay.check_ip(client_ip):
            current_app.logger.fatal('ip not allow, client_ip: %s, data: %s', client_ip, request.args)
            return BaseResponse('FAIlURE')

        # 签名验证
        if not CallbackPonypay.check_sign(form):
            current_app.logger.fatal('invalid sign, client_ip: %s, data: %s', client_ip, request.args)
            return BaseResponse('FAIlURE')

        order = DepositTransactionCtl.get_order(tx_id)
        if not order:
            return BaseResponse('FAIlURE')

        if status == '1':
            # 支付成功
            if not DepositTransactionCtl.success_order_process(order, tx_amount, channel_tx_id):
                return BaseResponse('FAIlURE')
        else:
            # 支付失败
            if not DepositTransactionCtl.failed_order_process(order, tx_amount, channel_tx_id):
                return BaseResponse('FAIlURE')

        return BaseResponse('SUCCESS')


@ns.route('/ponypay/withdraw')
class PonypayWithdraw(Resource):

    def get(self):
        """
        立马付充值回调
        :return:
        """
        if not EnvironEnum.is_local_evn(current_app.config['FLASK_ENV']):
            # 无论如何都记录一条log
            current_app.logger.info('ponypay withdraw callback, ip: %s, data: %s', IpKit.get_remote_ip(),
                                     request.args)

        form, error = PonyPayWithdrawForm().request_validate()
        if error:
            current_app.logger.fatal('msg: %s, data: %s', error.message, request.args)
            return BaseResponse('FAIlURE')

        # 交易订单id
        tx_id = form.corderid.data
        # 实际支付金额
        tx_amount = Decimal(form.money.data)
        # 订单状态： 成功/失败
        status = form.status.data
        # 签名
        sign = form.sign.data
        # 客户端IP
        client_ip = form.client_ip.data

        order = WithdrawTransactionCtl.get_order(tx_id)
        if not order:
            return BaseResponse('FAIlURE')

        channel_config = ChannelConfig.query_by_channel_id(order.channel_id)
        controller = WithdrawCallbackPonypay(channel_config.channel_enum)

        # IP白名单校验
        if not controller.check_ip(client_ip):
            current_app.logger.fatal('ip not allow, client_ip: %s, data: %s', client_ip, request.args)
            return BaseResponse('FAIlURE')

        # 签名验证
        if not controller.check_sign(tx_id, tx_amount, sign):
            current_app.logger.fatal('invalid sign, client_ip: %s, data: %s', client_ip, request.args)
            return BaseResponse('FAIlURE')

        if status == '1':
            # 支付成功
            if not WithdrawTransactionCtl.order_success(order, tx_amount):
                return BaseResponse('FAIlURE')
        else:
            # 支付失败
            if not WithdrawTransactionCtl.order_fail(order):
                return BaseResponse('FAIlURE')

        return BaseResponse('SUCCESS')
