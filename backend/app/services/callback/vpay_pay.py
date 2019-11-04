import json

from werkzeug.wrappers import BaseResponse
import decimal
from app.channel.vpay.deposit.callback import CallbackVpay
from app.libs.doc_response import ResponseDoc
from app.logics.transaction.deposit_ctl import DepositTransactionCtl

from app.logics.transaction.withdraw_ctl import WithdrawTransactionCtl
from . import api
from flask_restplus import Resource
from flask import current_app, request
from app.libs.ip_kit import IpKit

ns = api.namespace('callback', description='用户充值')


@ns.route('/vpay/deposit')
@ResponseDoc.response(ns, api)
class VpayDeposit(Resource):

    def post(self):
        client_ip = IpKit.get_remote_ip()

        current_app.logger.info('vpay deposit callback, ip: %s, data: %s', IpKit.get_remote_ip(), request.json)

        if not CallbackVpay.check_ip(client_ip):
            current_app.logger.fatal('ip not allow, client_ip: %s, data: %s, body: %s', client_ip, request.args,
                                     request.form)
            return BaseResponse('{"code": "00"}')

        resp_body = request.json
        sign = resp_body.pop("sign")
        sorted_params = sorted(list(resp_body.keys()))
        ac_amount = "{:.2f}".format(resp_body['actual_amount'])
        tx_amount = "{:.2f}".format(resp_body['original_amount'])
        resp_body['actual_amount'] = ac_amount
        resp_body['original_amount'] = tx_amount

        sign_str = "&".join(["{}={}".format(k, resp_body[k]) for k in sorted_params if resp_body.get(k, False)])
        flag = CallbackVpay.check_sign(sign, sign_str)

        if not flag:
            current_app.logger.fatal('invalid sign, data: %s, sign: %s, data: %s', client_ip, sign, sign_str)
            return BaseResponse('{"code": "01"}')

        tx_id = resp_body['company_order_id']
        order = DepositTransactionCtl.get_order(tx_id)
        if not order:
            return BaseResponse('{"code": "00"}')

        tx_amount = request.json['actual_amount']
        channel_tx_id = request.json['order_no']

        if not DepositTransactionCtl.success_order_process(order, decimal.Decimal(tx_amount), channel_tx_id):
            return BaseResponse('{"code": "00"}')
        return BaseResponse('{"code": "200"}')
