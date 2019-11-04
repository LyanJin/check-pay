from werkzeug.wrappers import BaseResponse
import decimal

from app.channel.epaytong.deposit.callback import CallbackEpayTong
from app.channel.onepay.deposit.callback import CallbackOnePay
from app.enums.third_config import ThirdPayConfig
from app.libs.doc_response import ResponseDoc
from app.libs.error_code import ResponseSuccess
from app.logics.transaction.deposit_ctl import DepositTransactionCtl
from app.logics.transaction.withdraw_ctl import WithdrawTransactionCtl
from . import api
from flask_restplus import Resource
from config import EnvironEnum
from flask import current_app, request
from app.libs.ip_kit import IpKit

ns = api.namespace('callback', description='用户充值')


@ns.route('/epaytong/deposit')
@ResponseDoc.response(ns, api)
class EpayTongDeposit(Resource):

    def post(self):
        client_ip = IpKit.get_remote_ip()
        third_config = ThirdPayConfig.EpayTong_PAY_DEPOSIT.value

        if not EnvironEnum.is_local_evn(current_app.config['FLASK_ENV']):
            # 无论如何都记录一条log
            current_app.logger.info('epaytong deposit callback, ip: %s, data: %s', IpKit.get_remote_ip(), request.form)

        if not CallbackEpayTong.check_ip(client_ip):
            current_app.logger.fatal('ip not allow, client_ip: %s, data: %s, body: %s', client_ip, request.args,
                                     request.form)
            return BaseResponse('FAIlURE')

        sys_tx_id = request.form['order_no']
        order = DepositTransactionCtl.get_order(sys_tx_id)
        if not order:
            current_app.logger.error('epaytong: no found order, order id: %s' % (sys_tx_id))
            return BaseResponse('FAILURE')

        no_need_field = ['signType', 'sign']
        sorted_fields = sorted([k for k in request.form.keys()])
        request_str = "&".join(
            ["{}={}".format(k, request.form[k]) for k in sorted_fields if
             (request.form[k] == 0 or request.form[k] == "0" or request.form[k]) and k not in no_need_field])
        sign = request.form['sign']
        sign_str = request_str + third_config['secret_key']
        flag = CallbackEpayTong.check_sign(sign, sign_str)

        if not flag:
            current_app.logger.fatal('invalid sign, client_ip: %s, data: %s, body: %s', client_ip, request.args,
                                     request_str)
            return ResponseSuccess(code=500, message='签名错误').as_response()

        tx_amount = request.form['price']
        pwTradeId = request.form['notify_id']

        status = request.form['is_success']
        trade = request.form['trade_status']
        if status == 'T' and trade == "TRADE_FINISHED":
            if not DepositTransactionCtl.success_order_process(order, decimal.Decimal(tx_amount), pwTradeId):
                return BaseResponse('FAIlURE')
        else:
            if not DepositTransactionCtl.failed_order_process(order, decimal.Decimal(tx_amount), pwTradeId):
                return BaseResponse('FAIlURE')

        return BaseResponse('success')
