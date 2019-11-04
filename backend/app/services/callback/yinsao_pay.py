from decimal import Decimal

from werkzeug.wrappers import BaseResponse

from app.channel.yinsao.deposit.callback import CallbackYinSao
from app.forms.deposit_channel_notify_form import YinSaoForm
from app.libs.ip_kit import IpKit
from app.logics.transaction.deposit_ctl import DepositTransactionCtl
from app.logics.transaction.withdraw_ctl import WithdrawTransactionCtl
from . import api
from flask_restplus import Resource
from app.libs.doc_response import ResponseDoc
from config import EnvironEnum
from flask import current_app, request

ns = api.namespace('callback', description='用户充值')


@ns.route('/yinsao/deposit')
@ResponseDoc.response(ns, api)
class YinSaoDeposit(Resource):

    def post(self):
        if not EnvironEnum.is_local_evn(current_app.config['FLASK_ENV']):
            # 无论如何都记录一条log
            current_app.logger.info('yinsao withdraw callback, ip: %s, data: %s, headers: %s', IpKit.get_remote_ip(),
                                     request.form, request.headers)

        data = {k: v for k, v in request.form.items()}

        client_ip = IpKit.get_remote_ip()

        if not CallbackYinSao.check_ip(client_ip):
            current_app.logger.fatal('ip not allow, client_ip: %s, data: %s', client_ip, request.args)
            return BaseResponse('FAIlURE')

        tx_amount = Decimal(data['transAmt']) / Decimal('100')
        sys_tx_id = data['orderNo']
        signature = data.pop('signature')
        key_list = sorted(list(data.keys()))
        request_str = "&".join(["{}={}".format(field, data[field]) for field in key_list if field != "risk"])
        sign = CallbackYinSao.generate_sign(request_str)
        flag = CallbackYinSao.check_sign(signature, sign)
        if not flag:
            current_app.logger.error('invalid sign, data:%s, sign:%s, signature:%s', data, sign, signature)
            return BaseResponse('FAIlURE')

        order = DepositTransactionCtl.get_order(sys_tx_id)
        if not order:
            current_app.logger.error('YinSao: no found order, order id: %s' % (sys_tx_id))
            return BaseResponse('FAILURE')

        if str(data['respCode']) == '0000':
            # 支付成功
            if not DepositTransactionCtl.success_order_process(order, tx_amount, ''):
                return BaseResponse('FAILURE')
        else:
            # 支付失败
            if not DepositTransactionCtl.failed_order_process(order, tx_amount, ''):
                return BaseResponse('FAIlURE')

        return BaseResponse('SUCCESS')


@ns.route('/yinsao/withdraw')
@ResponseDoc.response(ns, api)
class YinSaoWithDraw(Resource):
    def post(self):
        if not EnvironEnum.is_local_evn(current_app.config['FLASK_ENV']):
            # 无论如何都记录一条log
            current_app.logger.info('yinsao withdraw callback, ip: %s, data: %s, headers: %s', IpKit.get_remote_ip(),
                                    request.form, request.headers)

        # form, error = YinSaoForm.request_validate()
        # if error:
        #     current_app.logger.fatal('msg: %s, data: %s', error.message, request.json)
        #     return BaseResponse('FAIlURE')

        client_ip = IpKit.get_remote_ip()

        if not CallbackYinSao.check_ip(client_ip):
            current_app.logger.fatal('ip not allow, client_ip: %s, data: %s', client_ip, request.args)
            return BaseResponse('FAIlURE')

        data = {k: v for k, v in request.form.items()}

        tx_amount = Decimal(data['transAmt']) / Decimal('100')
        sys_tx_id = data['orderNo']

        signature = data.pop('signature')
        key_list = sorted(list(data.keys()))
        request_str = "&".join(["{}={}".format(field, data[field]) for field in key_list if field != "risk"])
        sign = CallbackYinSao.generate_sign(request_str)
        flag = CallbackYinSao.check_sign(signature, sign)

        if not flag:
            current_app.logger.fatal('invalid sign, data: %s, sign: %s, signature: %s', client_ip, data, sign, signature)
            return BaseResponse('FAIlURE')

        order = WithdrawTransactionCtl.get_order(sys_tx_id)
        if not order:
            return BaseResponse('FAIlURE')

        if str(data['respCode']) == '0000':
            # 支付成功
            if not WithdrawTransactionCtl.order_success(order, tx_amount):
                return BaseResponse('FAILURE')
        else:
            # 支付失败
            if not WithdrawTransactionCtl.order_fail(order):
                return BaseResponse('FAIlURE')

        return BaseResponse('SUCCESS')
