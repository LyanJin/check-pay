from decimal import Decimal

from flask import current_app, request
from werkzeug.wrappers import BaseResponse

from app.channel.rukoumy.deposit.callback import CallbackRuKouMy
from app.enums.trade import OrderStateEnum
from app.libs.doc_response import ResponseDoc
from app.libs.ip_kit import IpKit
from app.logics.transaction.deposit_ctl import DepositTransactionCtl
from config import EnvironEnum
from . import api
from flask_restplus import Resource

ns = api.namespace('callback', description='用户充值')


@ns.route('/rukoumy/deposit')
@ResponseDoc.response(ns, api)
class RuKouMyDeposit(Resource):

    def post(self):
        """
        RuKouMy，充值回调
        :return:
        """
        client_ip = IpKit.get_remote_ip()

        if not EnvironEnum.is_local_evn(current_app.config['FLASK_ENV']):
            # 无论如何都记录一条log
            current_app.logger.info('RuKouMy deposit callback, ip: %s, json: %s', IpKit.get_remote_ip(), request.json)

        if not CallbackRuKouMy.check_ip(client_ip):
            current_app.logger.error('ip not allow, client_ip: %s, data: %s, body: %s', client_ip, request.args,
                                    request.json)
            return BaseResponse('error')

        resp_body = request.json

        sign = resp_body.pop("sign")
        sorted_params = sorted(list(resp_body.keys()))
        resp_body['real_amount'] = "{:.2f}".format(int(resp_body['real_amount']))
        resp_body['pay_amount'] = "{:.2f}".format(int(resp_body['pay_amount']))

        sign_str = "&".join(
            ["{}={}".format(k, resp_body[k]) for k in sorted_params if resp_body.get(k, False) or k in ["code"]])

        flag = CallbackRuKouMy.check_sign(sign, sign_str)
        if not flag:
            current_app.logger.error('invalid sign, data: %s, sign: %s, data: %s', client_ip, sign, sign_str)
            return BaseResponse('error')

        order_id = resp_body['order_id']
        order = DepositTransactionCtl.get_order(order_id)

        if not order:
            return BaseResponse('success')

        if order.state.name == OrderStateEnum.SUCCESS.name:
            return BaseResponse('success')

        tx_amount = Decimal(str(request.json['real_amount']))
        channel_tx_id = request.json['order_no']

        code = resp_body['code']
        if code == 0:
            # 支付成功
            if not DepositTransactionCtl.success_order_process(order, tx_amount, channel_tx_id):
                return BaseResponse('error')
        else:
            # 支付失败
            if not DepositTransactionCtl.failed_order_process(order, tx_amount, channel_tx_id):
                return BaseResponse('error')

        return BaseResponse('success')
