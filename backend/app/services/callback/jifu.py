from decimal import Decimal

from flask import current_app, request
from werkzeug.wrappers import BaseResponse

from app.channel.jifu.deposit.callback import DepositCallbackJifu
from app.enums.channel import ChannelConfigEnum
from app.forms.deposit_channel_notify_form import JifuCallbackForm
from app.libs.doc_response import ResponseDoc
from app.libs.ip_kit import IpKit
from app.logics.transaction.deposit_ctl import DepositTransactionCtl
from config import EnvironEnum
from . import api
from flask_restplus import Resource

ns = api.namespace('callback', description='用户充值')


@ns.route('/jifu/deposit')
@ResponseDoc.response(ns, api)
class JifuDeposit(Resource):

    def post(self):
        """
        极付，充值回调，极付的回调只会只订单成功后才通知，如果处理失败，通道侧会每隔十秒重新请求一次，共请求十次
        :return:
        """
        if not EnvironEnum.is_local_evn(current_app.config['FLASK_ENV']):
            # 无论如何都记录一条log
            current_app.logger.info('jifu deposit callback, ip: %s, data: %s', IpKit.get_remote_ip(), request.form)

        form, error = JifuCallbackForm().request_validate()
        if error:
            current_app.logger.fatal('msg: %s, data: %s', error.message, request.form)
            return BaseResponse(error.message)

        # 交易订单id
        sys_tx_id = form.remark.data
        # 通道订单id
        channel_tx_id = form.id.data
        # 实际支付金额
        tx_amount = Decimal(form.money.data)
        # 客户端IP
        client_ip = form.client_ip.data

        # IP白名单校验
        checker = DepositCallbackJifu(ChannelConfigEnum.CHANNEL_7001)
        if not checker.check_ip(client_ip):
            current_app.logger.fatal('ip not allow, client_ip: %s, data: %s', client_ip, form.form_data)
            return BaseResponse('ip not allow')

        # 签名验证
        if not checker.check_sign(form.get_sign_fields(), form.get_raw_sign()):
            current_app.logger.fatal('invalid sign, client_ip: %s, data: %s', client_ip, form.form_data)
            return BaseResponse('invalid sign')

        order = DepositTransactionCtl.get_order(sys_tx_id)
        if not order:
            return BaseResponse('no order found for sys_tx_id: %s', sys_tx_id)

        if order.channel_tx_id != channel_tx_id:
            # 根据API文档的建议，之前已经将code放入数据库的channel_tx_id中，等回调时拿来比对
            current_app.logger.fatal('invalid channel_tx_id, client_ip: %s, channel_tx_id: %s, data: %s',
                                     client_ip, order.channel_tx_id, form.form_data)
            return BaseResponse('invalid channel_tx_id')

        # 支付成功
        if not DepositTransactionCtl.success_order_process(order, tx_amount, channel_tx_id):
            return BaseResponse('order process failed, sys_tx_id: %s', sys_tx_id)

        # 成功返回小写字符串success
        return BaseResponse('success')
