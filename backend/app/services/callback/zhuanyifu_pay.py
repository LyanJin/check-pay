from decimal import Decimal
from flask import current_app, request
from werkzeug.wrappers import BaseResponse
from app.channel.zhuanyifu.deposit.callback import CallbackZYF
from app.enums.trade import OrderStateEnum
from app.forms.deposit_channel_notify_form import ZhuanYeFuWithdrawForm
from app.libs.crypto import CryptoKit
from app.libs.doc_response import ResponseDoc
from app.libs.error_code import ResponseSuccess
from app.libs.ip_kit import IpKit
from app.logics.order.fee_calculator import FeeCalculator
from app.logics.transaction.deposit_ctl import DepositTransactionCtl
from app.logics.transaction.withdraw_ctl import WithdrawTransactionCtl
from app.models.channel import ChannelConfig, ProxyChannelConfig
from . import api
from flask_restplus import Resource
from config import EnvironEnum

ns = api.namespace('callback', description='用户充值')


@ns.route('/zhuanyifu/deposit')
@ResponseDoc.response(ns, api)
class ZYFDeposit(Resource):

    def post(self):
        if not EnvironEnum.is_local_evn(current_app.config['FLASK_ENV']):
            # 无论如何都记录一条log
            current_app.logger.info('zhuanyifu deposit callback, ip: %s, data: %s, headers: %s', IpKit.get_remote_ip(),
                                     request.json, request.headers)
        event = request.headers.get('ChinaRailway-Event')
        signature = request.headers.get('ChinaRailway-Signature')
        form, error = ZhuanYeFuWithdrawForm().request_validate()
        if error:
            current_app.logger.fatal('msg: %s, data: %s', error.message, request.args)
            return BaseResponse('FAIlURE')

        client_ip = form.client_ip.data
        tx_amount = Decimal(form.amount.data)
        fee = Decimal(form.fee.data)
        channel_tx_id = form.transaction.data

        # if not CallbackZYF.check_ip(client_ip):
        #     current_app.logger.fatal('ip not allow, client_ip: %s, data: %s, body: %s', client_ip, request.args,
        #                              request.json)
        #     return ResponseSuccess(code=500, message='ip not allow').as_response()

        pp = signature.split('.')
        if event != "Charge.Succeeded":
            return ResponseSuccess(code=500).as_response()

        order = DepositTransactionCtl.get_order(form.order.data)
        if not order:
            return ResponseSuccess(code=500, message='curr order no found').as_response()

        curr_status = order.state
        if curr_status != OrderStateEnum.INIT:
            return ResponseSuccess(code=500, message='curr order status must be DEALING').as_response()

        channel_config = ChannelConfig.query_by_channel_id(order.channel_id)
        # 检查通道手续费与系统计算出的手续费
        channel_cost = FeeCalculator.calc_cost(order.amount, channel_config.fee_type, channel_config.fee)
        if Decimal(fee) != channel_cost:
            current_app.logger.error(
                "ZYF deposit fee info order_id:{}, channel_fee: {}, channel_cost:{}".format(order.order_id,
                                                                                            Decimal(fee),
                                                                                            channel_cost))
        flag = CallbackZYF.check_sign(pp=pp, channel_config=channel_config)
        if not flag:
            current_app.logger.fatal('invalid sign, client_ip: %s, data: %s, body: %s', client_ip, request.args,
                                     request.json)
            return ResponseSuccess(code=500, message='签名错误').as_response()

        status = form.status.data

        if str(status) == '1':
            if not DepositTransactionCtl.success_order_process(order, tx_amount, channel_tx_id, client_ip):
                return ResponseSuccess(code=500, message='订单状态更新失败').as_response()
            else:
                return ResponseSuccess(code=500, message='签名错误').as_response()

        elif str(status) == '2':
            if not DepositTransactionCtl.failed_order_process(order, tx_amount, channel_tx_id, client_ip):
                return ResponseSuccess(code=500, message='订单状态更新失败').as_response()

        elif str(status) == '0':
            pass

        return ResponseSuccess(code=204).as_response()


@ns.route('/zhuanyifu/withdraw')
class ZhuanyifuWithdraw(Resource):

    def post(self):
        """
        专一付代付回调
        :return:
        """
        if not EnvironEnum.is_local_evn(current_app.config['FLASK_ENV']):
            # 无论如何都记录一条log
            current_app.logger.info('zhuanyifu withdraw callback, ip: %s, data: %s, headers: %s', IpKit.get_remote_ip(),
                                    request.json, request.headers)

        event = request.headers.get('ChinaRailway-Event')
        signature = request.headers.get('ChinaRailway-Signature')

        form, error = ZhuanYeFuWithdrawForm().request_validate()
        if error:
            current_app.logger.fatal('msg: %s, data: %s', error.message, request.args)
            return BaseResponse('FAIlURE')

        pp = signature.split('.')

        if event != "Pay.Succeeded":
            return ResponseSuccess(code=500).as_response()

        # 交易ID
        tx_id = form.order.data
        fee = Decimal(form.fee.data)
        order = WithdrawTransactionCtl.get_order(tx_id)
        if not order:
            return ResponseSuccess(code=500, message='curr order no found').as_response()

        curr_status = order.state
        if curr_status != OrderStateEnum.DEALING:
            return ResponseSuccess(code=500, message='curr order status must be DEALING').as_response()

        print(order.channel_id, form.order.data, order.merchant, order.create_time, order.order_id, order.uid)

        channel_config = ProxyChannelConfig.query_by_channel_id(order.channel_id)
        channel_cost = FeeCalculator.calc_cost(order.amount, channel_config.fee_type, channel_config.fee)
        if fee != channel_cost:
            current_app.logger.error(
                "ZYF withdraw fee info order_id:{}, channel_fee: {}, channel_cost:{}".format(order.order_id,
                                                                                             fee,
                                                                                             channel_cost))

        try:
            flag = CryptoKit.rsa_verify(pp[1], pp[0], channel_config.channel_enum.conf['plat_public_key'])
            if flag != True:
                return ResponseSuccess(code=500, message='签名错误').as_response()
        except Exception as e:
            return ResponseSuccess(code=500).as_response()

        # 代付金额
        tx_amount = Decimal(form.amount.data)
        # 代付费率
        fee = Decimal(form.fee.data)
        # 通道订单号
        transaction = form.transaction.data
        client_ip = form.client_ip.data
        status = form.status.data

        if str(status) == "1":
            """
            修改订单状态， 记录代付费率
            """
            if not WithdrawTransactionCtl.order_success(order, tx_amount):
                return ResponseSuccess(code=500).as_response()

        elif str(status) == "2":
            """
            代付订单失败， 
            1.给用户退款，给商户退款+手续费
            2. 修改订单状态 
            """
            # order = WithdrawTransactionCtl.get_order(merchant, order_id)
            if not WithdrawTransactionCtl.order_fail(order):
                return ResponseSuccess(code=500).as_response()

        return ResponseSuccess(code=204).as_response()
