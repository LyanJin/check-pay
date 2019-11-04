"""
充值
"""
from flask import current_app, url_for, request
from flask_restplus import Resource

from app.docs.doc_gateway.gateway_withdraw import DocRequestWithdraw, GatewayResponseWithdraw
from app.forms.gateway.withdraw_request import WithdrawRequestForm
from app.libs.doc_response import ResponseDoc
from app.libs.error_code import GatewaySignError, GatewayIPError, GatewayChannelError, GatewayWithdrawError, \
    ResponseSuccess
from app.libs.ip_kit import IpKit
from app.logics.gateway.form_deposit import GatewayFormChecker
from app.logics.transaction.withdraw_ctl import WithdrawTransactionCtl
from app.models.bankcard import BankCard
from config import EnvironEnum
from . import api

ResponseSuccess.doc_path = False
ns = api.namespace('withdraw', description='提现')


@ns.route('/request', endpoint='gateway_withdraw_request')
@ResponseDoc.response(ns, api, [
    GatewaySignError, GatewayIPError, GatewayChannelError, GatewayWithdrawError
], login=False, default=False)
class GatewayWithdrawRequest(Resource):

    @ns.expect(DocRequestWithdraw)
    @ns.marshal_with(GatewayResponseWithdraw.gen_doc(api))
    def post(self):
        """
        充值请求
        """
        if not EnvironEnum.is_local_evn(current_app.config['FLASK_ENV']):
            # 无论如何都记录一条log
            current_app.logger.info('path: %s, ip: %s, args: %s, data: %s',
                                     url_for("gateway_withdraw_request"), IpKit.get_remote_ip(), request.args,
                                     request.json)

        form, error = WithdrawRequestForm.request_validate()
        if error:
            return error.as_response()

        checker = GatewayFormChecker(form.merchant_id.data)

        # 1. IP白名单校验
        if not checker.verify_ip(form.client_ip.data):
            current_app.logger.error('msg: %s, ip: %s, white ips: %s', GatewayIPError.message, IpKit.get_remote_ip(),
                                     checker.get_white_ips())
            return GatewayIPError().as_response()

        # 2. 签名校验
        sign_fields = form.get_sign_fields()
        if not checker.verify_sign(form.sign.data, sign_fields):
            current_app.logger.error('msg: %s, sign: %s, fields: %s, sign_str: %s',
                                     GatewaySignError.message, form.sign.data, sign_fields,
                                     checker.get_sign_str(sign_fields))
            return GatewaySignError().as_response()

        # 3. 获取用户对象
        user = checker.get_fake_user(form.user_id.data)

        # 银行卡信息
        bank_info = BankCard.generate_model(
            bank_name=form.bank_type.data.desc,
            bank_code=form.bank_type.data.bank_code,
            card_no=form.card_no.data,
            account_name=form.account_name.data,
            branch=form.branch.data or '',
            province=form.province.data or '',
            city=form.city.data or '',
        )

        # 4. 创建订单
        order, error = WithdrawTransactionCtl.order_create(
            user=user,
            amount=form.amount.data,
            client_ip=form.user_ip.data,
            notify_url=form.notify_url.data,
            mch_tx_id=form.mch_tx_id.data,
            bank_info=bank_info.bank_info_dict,
            extra=form.extra.data,
        )
        if error:
            return error.as_response()

        return GatewayResponseWithdraw(bs_data=dict(
            sys_tx_id=order.sys_tx_id,
            mch_tx_id=order.mch_tx_id,
        )).as_response()

