from werkzeug.wrappers import BaseResponse
import decimal
from app.channel.gpay.deposit.callback import CallbackGpay
from app.enums.trade import OrderStateEnum
from app.libs.doc_response import ResponseDoc
from app.logics.transaction.deposit_ctl import DepositTransactionCtl
from . import api
from flask_restplus import Resource
from config import EnvironEnum
from flask import current_app, request
from app.libs.ip_kit import IpKit

ns = api.namespace('callback', description='用户充值')


@ns.route('/gpay/deposit')
@ResponseDoc.response(ns, api)
class GPayDeposit(Resource):

    def post(self):
        client_ip = IpKit.get_remote_ip()

        if not EnvironEnum.is_local_evn(current_app.config['FLASK_ENV']):
            # 无论如何都记录一条log
            current_app.logger.info('Gpay deposit callback, ip: %s, data: %s', IpKit.get_remote_ip(), request.form)

        sys_tx_id = request.form['company_order_num']
        tx_amount = request.form['amount']
        pw_trade_id = request.form['mownecum_order_num']

        if not CallbackGpay.check_ip(client_ip):
            current_app.logger.fatal('ip not allow, client_ip: %s, data: %s, body: %s', client_ip, request.args,
                                     request.form)
            return BaseResponse(
                '{"company_order_num":"%s", "mownecum_order_num":"%s", "status":"1", "error_msg":"%s"}' % (
                    sys_tx_id, pw_trade_id, "订单状态已更新"))

        order = DepositTransactionCtl.get_order(sys_tx_id)
        if not order:
            current_app.logger.error('gpay: no found order, order id: %s' % (sys_tx_id))
            return BaseResponse(
                '{"company_order_num":"%s", "mownecum_order_num":"%s", "status":"0", "error_msg":"%s"}' % (
                    sys_tx_id, pw_trade_id, "查不到该订单"))

        if order.state.name != OrderStateEnum.INIT.name:
            return BaseResponse(
                '{"company_order_num":"%s", "mownecum_order_num":"%s", "status":"1", "error_msg":"%s"}' % (
                    sys_tx_id, pw_trade_id, "订单状态已更新"))

        sorted_fields = ["pay_time", "bank_id", "amount", "company_order_num", "mownecum_order_num", "pay_card_num",
                         "pay_card_name", "channel", "area", "fee", "transaction_charge", "deposit_mode"]

        request_str = "".join([request.form.get(k, "") for k in sorted_fields])
        sign = request.form['key']
        flag = CallbackGpay.check_sign(sign, request_str)

        if not flag:
            current_app.logger.fatal('invalid sign, client_ip: %s, data: %s, body: %s', client_ip, request.args,
                                     request_str)
            return BaseResponse(
                '{"company_order_num":"%s", "mownecum_order_num":"%s", "status":"0", "error_msg":"%s"}' % (
                    sys_tx_id, pw_trade_id, "更新订单状态失败"))

        if not DepositTransactionCtl.success_order_process(order, decimal.Decimal(tx_amount), pw_trade_id):
            return BaseResponse(
                '{"company_order_num":"%s", "mownecum_order_num":"%s", "status":"0", "error_msg":"%s"}' % (
                    sys_tx_id, pw_trade_id, "更新订单状态失败"))

        return BaseResponse('{"company_order_num":"%s", "mownecum_order_num":"%s", "status":"1", "error_msg":""}' % (
            sys_tx_id, pw_trade_id))
