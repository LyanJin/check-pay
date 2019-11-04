# -*-coding:utf8-*-
from decimal import Decimal

from app.enums.account import UserPermissionEnum
from app.enums.third_enum import SdkRenderType
from app.enums.trade import PayTypeEnum, OrderSourceEnum, InterfaceTypeEnum
from app.extensions.ext_api import api_cashier as api
from flask_restplus import Resource

from app.forms.deposit_form import CreateOrderForm, AmountInputForm
from app.forms.domain_form import DomainForm
from app.libs.error_code import InvalidDepositPaymentTypeError, PreOrderCreateError, UserPermissionDeniedError
from app.libs.doc_response import ResponseDoc
from app.logics.channel.chanel_cache import ChannelLimitCacheCtl
from app.logics.channel.channel_list import ChannelListHelper
from app.logics.payment.deposit_helper import DepositHelper
from app.logics.token.cashier_token import cashier_decorators
from flask import g, current_app
from app.docs.doc_cashier.deposit_withdraw import ResponseDepositLimitConfig, ResponsePaymentType, \
    DepositRequest, ResponseRedirectUrl, PaymentTypeListRequestDoc

ns = api.namespace('deposit', description='用户充值')


@ns.route('/limit/config/get', endpoint='get_limit')
@ResponseDoc.response(ns, api)
class ResetPassword(Resource):
    method_decorators = cashier_decorators

    # 相应数据格式
    @ns.marshal_with(ResponseDepositLimitConfig.gen_doc(api))
    def post(self):
        """
        获取单笔交易最低最高限额
        """
        form, error = DomainForm().request_validate()
        if error:
            return error.as_response()

        merchant = form.merchant.data

        # limit_min, limit_max = ChannelLimitCacheCtl(PayTypeEnum.DEPOSIT).get_channel_limit()
        limit_min, limit_max = ChannelListHelper.get_channel_limit_range(
            merchant=merchant,
            payment_way=PayTypeEnum.DEPOSIT,
            client_ip=form.client_ip.data,
        )

        return ResponseDepositLimitConfig(bs_data=dict(
            limit_min=limit_min,
            limit_max=limit_max)
        ).as_response()


@ns.route('/payment/type/list', endpoint='payment_type')
@ResponseDoc.response(ns, api)
class PaymentTypeList(Resource):
    method_decorators = cashier_decorators

    @ns.expect(PaymentTypeListRequestDoc)
    @ns.marshal_with(ResponsePaymentType.gen_doc(api))
    def post(self):
        """
        获取当前可用的充值方式
        """
        form, error = AmountInputForm().request_validate()
        if error:
            return error.as_response()

        routers = ChannelListHelper.get_channel_payment_type_router(
            interface=InterfaceTypeEnum.CASHIER_H5,
            amount=form.amount.data,
            merchant=form.merchant.data,
            uid=g.user.uid,
        )

        channels = ChannelListHelper.get_available_channels(
            form.merchant.data,
            PayTypeEnum.DEPOSIT,
            client_ip=form.client_ip.data,
        )
        payment_type_list = ChannelListHelper.choice_one_channel_for_payment_type(
            channels,
            routers,
            form.merchant.data,
            form.amount.data,
        )

        return ResponsePaymentType(bs_data=dict(payment_type_list=payment_type_list)).as_response()


@ns.route('/order/create')
@ResponseDoc.response(ns, api)
class DepositOrderCreate(Resource):
    method_decorators = cashier_decorators

    @ns.expect(DepositRequest)
    @ns.marshal_with(ResponseRedirectUrl.gen_doc(api))
    def post(self):
        """
        充值订单 创建预支付订单
        :return:
        """
        form, error = CreateOrderForm().request_validate()
        if error:
            return error.as_response()

        channel_enum = form.channel_id.data
        payment_type = form.payment_type.data
        amount = Decimal(form.amount.data)

        if not g.user.has_permission(UserPermissionEnum.DEPOSIT):
            return UserPermissionDeniedError().as_response()

        # 判断当前传入的支付类型是否该渠道支持
        # print(payment_type, channel_enum.conf['payment_type'], '********************')
        if payment_type != channel_enum.conf['payment_type']:
            return InvalidDepositPaymentTypeError()

        # print(channel_enum.conf['provider'], channel_enum.conf['request_cls'], "****************")

        rst = DepositHelper.do_deposit_request(
            user=g.user,
            channel_enum=channel_enum,
            amount=amount,
            client_ip=form.client_ip.data,
            user_agent=form.user_agent.data,
            source=OrderSourceEnum.TESTING if g.user.is_test_user else OrderSourceEnum.ONLINE,
            in_type=InterfaceTypeEnum.CASHIER_H5,
        )
        if rst['error']:
            return PreOrderCreateError()

        ps_rst = DepositHelper.parse_result(
            data=rst['data'],
            order_id=rst['order'].order_id,
            endpoint='cashier_deposit_redirect',
            channel_enum=channel_enum,
        )

        return ResponseRedirectUrl(bs_data=dict(
            redirect_url=ps_rst['redirect_url'],
            pay_type=SdkRenderType.URL,
        )).as_response()


@ns.route('/redirect', endpoint="cashier_deposit_redirect")
class DepositOrderSelect(Resource):

    def get(self):
        """
        渲染支付页面
        :return:
        """
        return DepositHelper.render_page()
