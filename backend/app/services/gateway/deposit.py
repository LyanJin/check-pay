"""
充值
"""
from flask import current_app, request, url_for
from flask_restplus import Resource

from app.docs.doc_gateway.gateway_deposit import DocRequestDeposit, GatewayResponseDeposit, DocOrderNotify
from app.enums.trade import PayTypeEnum, OrderSourceEnum, InterfaceTypeEnum
from app.forms.gateway.deposit_request import DepositRequestForm, DepositNotifyForm
from app.libs.doc_response import ResponseDoc
from app.libs.error_code import GatewaySignError, GatewayIPError, GatewayChannelError, GatewayDepositError, \
    ResponseSuccess
from app.libs.ip_kit import IpKit
from app.logics.channel.channel_list import ChannelListHelper
from app.logics.gateway.form_deposit import GatewayFormChecker
from app.logics.payment.deposit_helper import DepositHelper
from config import EnvironEnum
from . import api

ResponseSuccess.doc_path = False
ns = api.namespace('deposit', description='充值')


@ns.route('/request', endpoint='gateway_deposit_request')
@ResponseDoc.response(ns, api, [
    GatewaySignError, GatewayIPError, GatewayChannelError, GatewayDepositError
], login=False, default=False)
class GatewayDepositRequest(Resource):

    @ns.expect(DocRequestDeposit)
    @ns.marshal_with(GatewayResponseDeposit.gen_doc(api))
    def post(self):
        """
        充值请求
        """
        if not EnvironEnum.is_local_evn(current_app.config['FLASK_ENV']):
            # 无论如何都记录一条log
            current_app.logger.info('path: %s, ip: %s, args: %s, data: %s',
                                     url_for("gateway_deposit_request"), IpKit.get_remote_ip(), request.args,
                                     request.json)

        form, error = DepositRequestForm.request_validate()
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

        # 3. 获取对应支付方式下的充值通道
        channel = ChannelListHelper.get_one_channel_by_payment_type(
            merchant=form.merchant_id.data,
            payment_type=form.payment_type.data,
            amount=form.amount.data,
            client_ip=form.user_ip.data,
        )
        if not channel:
            current_app.logger.error("no channel found, request data: %s", form.get_data())
            return GatewayChannelError().as_response()

        # # 境外IP检查
        # if channel.is_ip_forbidden(form.user_ip.data):
        #     return GatewayDepositError(message="此通道不支持境外IP，请使用VPN后重试").as_response()

        # 4. 获取用户对象
        user = checker.get_fake_user(form.user_id.data)

        # 5. 发起支付
        rst = DepositHelper.do_deposit_request(
            client_ip=form.user_ip.data,
            user_agent=form.user_agent.data,
            user=user,
            amount=form.amount.data,
            channel_enum=channel.channel_enum,
            notify_url=form.notify_url.data,
            result_url=form.result_url.data,
            mch_tx_id=form.mch_tx_id.data,
            extra=form.extra.data,
            source=OrderSourceEnum.TESTING if form.merchant_id.data.is_test else OrderSourceEnum.ONLINE,
            in_type=InterfaceTypeEnum.API,
        )
        if rst['error']:
            return GatewayDepositError(message=rst['error'])

        # 6. 解析URL
        ps_rst = DepositHelper.parse_result(
            data=rst['data'],
            order_id=rst['order'].order_id,
            endpoint='gateway_deposit_redirect',
            channel_enum=channel.channel_enum,
        )

        return GatewayResponseDeposit(bs_data=dict(
            redirect_url=ps_rst['redirect_url'],
            valid_time=ps_rst['valid_time'],
            sys_tx_id=rst['order'].sys_tx_id,
            mch_tx_id=rst['order'].mch_tx_id,
        )).as_response()


@ns.route('/redirect', endpoint="gateway_deposit_redirect")
class GatewayDepositRedirect(Resource):

    def get(self):
        """
        渲染第三方跳转页面
        :return:
        """
        if not EnvironEnum.is_local_evn(current_app.config['FLASK_ENV']):
            # 无论如何都记录一条log
            current_app.logger.info('path: %s, ip: %s, args: %s, data: %s',
                                     url_for("gateway_deposit_redirect"), IpKit.get_remote_ip(), request.args,
                                     request.json)

        return DepositHelper.render_page()


@ns.route('/demo/notify', endpoint="gateway_demo_notify")
class GatewayDemoNotify(Resource):

    @ns.expect(DocOrderNotify)
    @ns.marshal_with(ResponseSuccess.gen_doc(api))
    def post(self):
        """
        发货通知，由商户实现
        :return:
        """
        if not EnvironEnum.is_local_evn(current_app.config['FLASK_ENV']):
            # 无论如何都记录一条log
            current_app.logger.info('path: %s, ip: %s, args: %s, data: %s',
                                     url_for("gateway_demo_notify"), IpKit.get_remote_ip(), request.args,
                                     request.json)

        form, error = DepositNotifyForm.request_validate()
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

        # 商户自己的业务逻辑处理
        current_app.logger.info('notify success: %s', form.json_data)

        return ResponseSuccess().as_response()
