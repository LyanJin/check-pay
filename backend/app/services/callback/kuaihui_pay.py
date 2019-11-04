from decimal import Decimal

from flask import current_app, request
from werkzeug.wrappers import BaseResponse

from app.enums.third_config import ThirdPayConfig
from app.forms.deposit_channel_notify_form import KhpayForm
from app.libs.doc_response import ResponseDoc
from app.libs.ip_kit import IpKit
from app.libs.order_kit import OrderUtils
from app.channel.kuaihui.deposit.callback import CallbackKhpay
from app.logics.transaction.deposit_ctl import DepositTransactionCtl
from app.logics.transaction.withdraw_ctl import WithdrawTransactionCtl
from app.models.channel import ChannelConfig
from config import EnvironEnum
from . import api
from flask_restplus import Resource

ns = api.namespace('callback', description='用户充值')


@ns.route('/kuaihui/deposit')
@ResponseDoc.response(ns, api)
class KhpayDeposit(Resource):

    def post(self):
        """
        快汇支付，充值回调
        :return:
        """
        if not EnvironEnum.is_local_evn(current_app.config['FLASK_ENV']):
            # 无论如何都记录一条log
            current_app.logger.info(
                'kuaihui deposit callback, ip: %s, args: %s, data: %s', IpKit.get_remote_ip(), request.args,
                request.json)

        form, error = KhpayForm().request_validate()
        if error:
            current_app.logger.fatal(
                'msg: %s, args: %s, data: %s', error.message, request.args, request.json)
            return BaseResponse(error.message)

        # 交易订单id
        tx_id = form.client_ordid.data
        # 充值通道 订单id
        channel_tx_id = form.ordid.data
        # 实际支付金额
        tx_amount = Decimal(form.amount.data)
        # 订单状态： 成功/失败
        status = form.status.data
        # 客户端IP
        client_ip = form.client_ip.data
        custid = form.custid.data
        kuai_hui_dict = {"PAY5f34c380-b8e6-11e9-9edc-511803f475f9": ThirdPayConfig.KUAIHUI.value,
                         "PAY5f34c380-b8e6-11e9-9edc-511803f475f9": ThirdPayConfig.KUAIHUI_0bd0d8.value}
        # 签名验证
        if not CallbackKhpay.check_sign(form, kuai_hui_dict[custid]):
            current_app.logger.fatal(
                'invalid sign, client_ip: %s, data: %s', client_ip, request.json)
            return BaseResponse('FAIlURE')

        # IP白名单校验
        if not CallbackKhpay.check_ip(client_ip):
            current_app.logger.fatal(
                'ip not allow, client_ip: %s, data: %s', client_ip, request.json)
            return BaseResponse('FAIlURE')

        order = DepositTransactionCtl.get_order(tx_id)
        if not order:
            return BaseResponse('FAIlURE')

        if order.state.is_final_state:
            # 已经通知了就返回成功
            return BaseResponse('{"status_code": 200}')

        if status == 'waiting':
            return BaseResponse('FAIlURE')

        if status == 'finish':
            # 支付成功
            if not DepositTransactionCtl.success_order_process(order, tx_amount, channel_tx_id):
                return BaseResponse('FAIlURE')
        else:
            # 支付失败
            if not DepositTransactionCtl.failed_order_process(order, tx_amount, channel_tx_id):
                return BaseResponse('FAIlURE')

        return BaseResponse('{"status_code": 200}')
