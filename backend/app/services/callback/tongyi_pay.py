from decimal import Decimal
from flask import current_app, request
from werkzeug.wrappers import BaseResponse

from app.channel.tongyi_pay.deposit.callback import CallbackTongYiPay
from app.enums.trade import OrderStateEnum
from app.libs.doc_response import ResponseDoc
from app.libs.error_code import ResponseSuccess
from app.libs.ip_kit import IpKit
from app.logics.transaction.deposit_ctl import DepositTransactionCtl
from . import api
from flask_restplus import Resource
from config import EnvironEnum

ns = api.namespace('callback', description='用户充值')


@ns.route('/tongyi/deposit')
@ResponseDoc.response(ns, api)
class TongYiDeposit(Resource):

    def get(self):
        """
        Tong yi Pay，充值回调
        :return:
        """
        if not EnvironEnum.is_local_evn(current_app.config['FLASK_ENV']):
            # 无论如何都记录一条log
            current_app.logger.info('tong yi deposit callback, ip: %s, data: %s', IpKit.get_remote_ip(), request.args)

        client_ip = IpKit.get_remote_ip()
        if not CallbackTongYiPay.check_ip(client_ip):
            current_app.logger.error('ip not allow, client_ip: %s, data: %s, body: %s', client_ip, request.args,
                                    request.json)

        sign = request.args.get("sign")
        keys = sorted(list(request.args.keys()))
        sign_str = "&".join(["{}={}".format(k, request.args.get(k)) for k in keys if k not in ['sign'] and request.args.get(k, False)])
        flag = CallbackTongYiPay.check_sign(sign, sign_str)
        if not flag:
            current_app.logger.error('invalid sign, client_ip: %s, data: %s, body: %s', client_ip, request.args,
                                     sign_str)
            return BaseResponse('error')

        order_id = request.args.get('order')

        order = DepositTransactionCtl.get_order(order_id)
        if not order:
            current_app.logger.error('invalid order: order_id: %s', order_id)
            return BaseResponse('FAIlURE')

        if order.state.name == OrderStateEnum.SUCCESS.name:
            return BaseResponse('SUCCESS')

        channel_tx_id = request.args.get('orderId', False)

        state = request.args.get('status', 0)
        tx_amount = request.args.get('money', 0)

        if str(state) == "2" or str(state) == "3":
            if not DepositTransactionCtl.success_order_process(order, Decimal(tx_amount), channel_tx_id):
                return BaseResponse('FAIlURE')

        return BaseResponse('SUCCESS')
