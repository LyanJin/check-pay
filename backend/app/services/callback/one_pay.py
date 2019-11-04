from werkzeug.wrappers import BaseResponse
import decimal
from app.channel.onepay.deposit.callback import CallbackOnePay
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


@ns.route('/onepay/result')
@ResponseDoc.response(ns, api)
class OnePayResult(Resource):

    def post(self):
        if not EnvironEnum.is_local_evn(current_app.config['FLASK_ENV']):
            # 无论如何都记录一条log
            current_app.logger.info('one pay result callback, ip: %s, data: %s, headers: %s, json data: %s', IpKit.get_remote_ip(),
                                     request.form, request.headers, request.json)

        client_ip = IpKit.get_remote_ip()

        if not CallbackOnePay.check_ip(client_ip):
            current_app.logger.fatal('ip not allow, client_ip: %s, data: %s', client_ip, request.args)
            return BaseResponse('FAIlURE')

        current_app.logger.info('one pay body: {}'.format("&".join(["{}={}".format(k, request.form[k]) for k, v in request.form.items()])))
        sys_tx_id = request.form['merchantTradeId']
        order = DepositTransactionCtl.get_order(sys_tx_id)
        if not order:
            current_app.logger.error('OnePay: no found order, order id: %s' % (sys_tx_id))
            return BaseResponse('FAILURE')

        no_need_field = ['signType', 'sign']
        sorted_fields = sorted([k for k in request.form.keys()])
        request_str = "&".join(
            ["{}={}".format(k, request.form[k]) for k in sorted_fields if k not in no_need_field and request.form[k]])
        sign = request.form['sign']

        flag = CallbackOnePay.check_sign(sign, request_str)

        if not flag:
            current_app.logger.fatal('invalid sign, client_ip: %s, data: %s, body: %s', client_ip, request.args,
                                     request_str)
            return ResponseSuccess(code=500, message='签名错误').as_response()

        tx_amount = request.form['amountFee']
        pwTradeId = request.form['pwTradeId']

        status = request.form['tradeStatus']
        if status == 'PS_PAYMENT_FAIL':
            if not DepositTransactionCtl.failed_order_process(order, tx_amount, pwTradeId):
                return BaseResponse('FAIlURE')

        return BaseResponse('SUCCESS')


@ns.route('/onepay/deposit')
@ResponseDoc.response(ns, api)
class OnePayDeposit(Resource):

    def post(self):
        if not EnvironEnum.is_local_evn(current_app.config['FLASK_ENV']):
            # 无论如何都记录一条log
            current_app.logger.info('one pay deposit callback, ip: %s, data: %s, headers: %s, json data:%s', IpKit.get_remote_ip(),
                                     request.form, request.headers, request.json)

        client_ip = IpKit.get_remote_ip()

        if not CallbackOnePay.check_ip(client_ip):
            current_app.logger.fatal('ip not allow, client_ip: %s, data: %s', client_ip, request.args)
            return BaseResponse('FAIlURE')

        sys_tx_id = request.form['merchantTradeId']
        order = DepositTransactionCtl.get_order(sys_tx_id)
        if not order:
            current_app.logger.error('OnePay: no found order, order id: %s' % (sys_tx_id))
            return BaseResponse('FAILURE')

        no_need_field = ['signType', 'sign']
        sorted_fields = sorted([k for k in request.form.keys()])
        request_str = "&".join(
            ["{}={}".format(k, request.form[k]) for k in sorted_fields if k not in no_need_field and request.form[k]])
        sign = request.form['sign']

        flag = CallbackOnePay.check_sign(sign, request_str)

        if not flag:
            current_app.logger.fatal('invalid sign, client_ip: %s, data: %s, body: %s', client_ip, request.args,
                                     request_str)
            return ResponseSuccess(code=500, message='签名错误').as_response()

        tx_amount = request.form['amountFee']
        pwTradeId = request.form['pwTradeId']

        status = request.form['tradeStatus']
        if status == 'PS_PAYMENT_FAIL':
            if not DepositTransactionCtl.failed_order_process(order, decimal.Decimal(tx_amount), pwTradeId):
                return BaseResponse('FAIlURE')
        elif status == 'PS_PAYMENT_SUCCESS':
            if not DepositTransactionCtl.success_order_process(order, decimal.Decimal(tx_amount), pwTradeId):
                return BaseResponse('FAIlURE')

        return BaseResponse('SUCCESS')


@ns.route('/onepay/cashier_deposit')
@ResponseDoc.response(ns, api)
class OnePayCashierDeposit(Resource):

    def post(self):
        if not EnvironEnum.is_local_evn(current_app.config['FLASK_ENV']):
            # 无论如何都记录一条log
            current_app.logger.info('one pay QR deposit callback, ip: %s, data: %s, headers: %s, json data:%s',
                                     IpKit.get_remote_ip(),
                                     request.form, request.headers, request.json)

        client_ip = IpKit.get_remote_ip()

        if not CallbackOnePay.check_ip(client_ip):
            current_app.logger.fatal('ip not allow, client_ip: %s, data: %s', client_ip, request.args)
            return BaseResponse('FAIlURE')

        sys_tx_id = request.form['order_no']
        order = DepositTransactionCtl.get_order(sys_tx_id)
        if not order:
            current_app.logger.error('OnePay: no found order, order id: %s' % (sys_tx_id))
            return BaseResponse('FAILURE')

        no_need_field = ['signType', 'sign']
        sorted_fields = sorted([k for k in request.form.keys()])
        request_str = "&".join(
            ["{}={}".format(k, request.form[k]) for k in sorted_fields if k not in no_need_field and request.form[k]])
        sign = request.form['sign']

        flag = CallbackOnePay.check_sign(sign, request_str)

        if not flag:
            current_app.logger.fatal('invalid sign, client_ip: %s, data: %s, body: %s', client_ip, request.args,
                                     request_str)
            return ResponseSuccess(code=500, message='签名错误').as_response()

        tx_amount = request.form['amount']
        pwTradeId = request.form['payment_id']

        status = request.form['status']
        if status == 'PS_PAYMENT_FAIL':
            if not DepositTransactionCtl.failed_order_process(order, decimal.Decimal(tx_amount), pwTradeId):
                return BaseResponse('FAIlURE')
        elif status == 'PS_PAYMENT_SUCCESS':
            if not DepositTransactionCtl.success_order_process(order, decimal.Decimal(tx_amount), pwTradeId):
                return BaseResponse('FAIlURE')

        return BaseResponse('SUCCESS')


@ns.route('/onepay/withdraw')
@ResponseDoc.response(ns, api)
class OnePayWithDraw(Resource):
    def post(self):
        if not EnvironEnum.is_local_evn(current_app.config['FLASK_ENV']):
            # 无论如何都记录一条log
            current_app.logger.info('onepay withdraw callback, ip: %s, headers: %s, json data: %s', IpKit.get_remote_ip(),
                                     request.headers, request.json)

        # form, error = YinSaoForm.request_validate()
        # if error:
        #     current_app.logger.fatal('msg: %s, data: %s', error.message, request.json)
        #     return BaseResponse('FAIlURE')

        current_app.logger.fatal('onepay withdraw callback, ip: %s, form data: %s, headers: %s, json data: %s',
                                IpKit.get_remote_ip(),
                                request.form, request.headers, request.json)

        client_ip = IpKit.get_remote_ip()

        if not CallbackOnePay.check_ip(client_ip):
            current_app.logger.fatal('ip not allow, client_ip: %s, data: %s', client_ip, request.args)
            return BaseResponse('FAIlURE')

        flag = request.json['flag']
        if flag == 'FAILED':
            return BaseResponse('FAIlURE')

        data = {k: v for k, v in request.json['data'].items()}
        no_need_sign = ['totalFactorage', 'sign', 'signType', 'detailList']

        signature = data.pop('sign')
        key_list = sorted(list(data.keys()))
        request_str = "&".join(["{}={}".format(field, data[field]) for field in key_list if
                                data.get(field, False) and field not in no_need_sign])

        flag = CallbackOnePay.check_sign(signature, request_str)

        if not flag:
            current_app.logger.fatal('invalid sign, data: %s, sign: %s, data: %s', client_ip, data, signature,
                                     request_str)
            return BaseResponse('FAIlURE')

        withdraw_order = request.json['data']['detailList'][0]
        tx_id = withdraw_order['serialNo']
        tx_amount = withdraw_order['amount']
        order = WithdrawTransactionCtl.get_order(tx_id)
        if not order:
            return BaseResponse('FAIlURE')

        if str(withdraw_order['tradeStatus']) == '1':
            # 支付成功
            if not WithdrawTransactionCtl.order_success(order, decimal.Decimal(tx_amount)):
                return BaseResponse('FAILURE')
        elif str(withdraw_order['tradeStatus']) == '2':
            # 支付失败
            if not WithdrawTransactionCtl.order_fail(order):
                return BaseResponse('FAIlURE')

        return BaseResponse('SUCCESS')
