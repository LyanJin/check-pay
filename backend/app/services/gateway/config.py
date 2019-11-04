"""
充值
"""
from flask import current_app, url_for, request
from flask_restplus import Resource

from app.docs.doc_gateway.gateway_config import DocRequestConfig, GatewayResponseConfig
from app.enums.trade import PaymentBankEnum, PayTypeEnum
from app.forms.gateway.deposit_config import DepositConfigForm
from app.libs.doc_response import ResponseDoc
from app.libs.error_code import GatewayIPError, GatewaySignError
from app.libs.ip_kit import IpKit
from app.logics.channel.chanel_cache import ChannelLimitCacheCtl
from app.logics.channel.channel_list import ChannelListHelper
from app.logics.gateway.form_deposit import GatewayFormChecker
from config import EnvironEnum
from . import api

ns = api.namespace('config', description='获取配置信息')


@ns.route('/get', endpoint="gateway_config_get")
@ResponseDoc.response(ns, api, [
    GatewayIPError, GatewaySignError
], login=False, default=False)
class GatewayConfigRequest(Resource):

    @ns.expect(DocRequestConfig)
    @ns.marshal_with(GatewayResponseConfig.gen_doc(api))
    def post(self):
        """
        充值请求
        """
        if not EnvironEnum.is_local_evn(current_app.config['FLASK_ENV']):
            # 无论如何都记录一条log
            current_app.logger.info('path: %s, ip: %s, args: %s, data: %s',
                                    url_for("gateway_config_get"), IpKit.get_remote_ip(), request.args,
                                    request.json)

        form, error = DepositConfigForm.request_validate()
        if error:
            return error.as_response()

        merchant = form.merchant_id.data

        checker = GatewayFormChecker(merchant)

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

        # 3. 返回可用的支付方式以及限额
        # 充值每种支付类型的限额
        payment_types = ChannelListHelper.get_channels_for_gateway(
            merchant,
            PayTypeEnum.DEPOSIT,
            client_ip=form.user_ip.data,
        )
        # 提现限额
        # limit_min, limit_max = ChannelLimitCacheCtl(PayTypeEnum.WITHDRAW).get_channel_limit()
        limit_min, limit_max = ChannelListHelper.get_channel_limit_range(
            merchant=merchant,
            payment_way=PayTypeEnum.WITHDRAW,
            client_ip=form.user_ip.data,
        )

        withdraw_config = dict(
            limit_min=limit_min,  # 最小限额列表的最小值
            limit_max=limit_max,  # 最大限额列表的最大值
        )

        return GatewayResponseConfig(bs_data=dict(
            payment_types=payment_types,
            withdraw_config=withdraw_config,
        )).as_response()
