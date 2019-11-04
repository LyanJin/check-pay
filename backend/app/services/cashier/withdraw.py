# -*-coding:utf8-*-
from decimal import Decimal

from app.caches.user_payment_password import UserPaymentPasswordLimitCache
from app.enums.account import UserPermissionEnum
from app.enums.trade import PayTypeEnum
from app.extensions.ext_api import api_cashier as api
from flask_restplus import Resource

from app.forms.deposit_form import CreateWithdrawOrderForm
from app.forms.domain_form import DomainForm
from app.libs.balance_kit import BalanceKit
from app.libs.doc_response import ResponseDoc
from app.logics.channel.chanel_cache import ChannelLimitCacheCtl
from app.logics.channel.channel_list import ChannelListHelper
from app.logics.token.cashier_token import cashier_decorators
from app.logics.transaction.withdraw_ctl import WithdrawTransactionCtl
from app.libs.error_code import ResponseSuccess, PaymentPasswordError, UserPermissionDeniedError
from flask import g
from app.docs.doc_cashier.deposit_withdraw import ResponseWithdrawLimitConfig, ResponseBankWithdraw, WithdrawRequestDoc
from app.models.balance import UserBalance
from app.models.user import User

ns = api.namespace('withdraw', description='用户提现')


@ns.route('/limit/config/get', endpoint='withdraw_get_limit')
@ResponseDoc.response(ns, api)
class ResetPassword(Resource):
    method_decorators = cashier_decorators

    # 相应数据格式
    @ns.marshal_with(ResponseWithdrawLimitConfig.gen_doc(api))
    def post(self):
        """
        获取单笔交易最低最高限额
        """
        form, error = DomainForm().request_validate()
        if error:
            return error.as_response()

        # 获取用户余额
        uid = g.user.uid
        merchant = g.user.merchant

        user_balance = UserBalance.query_balance(uid=uid, merchant=merchant).first()

        # limit_min, limit_max = ChannelLimitCacheCtl(PayTypeEnum.WITHDRAW).get_channel_limit()
        limit_min, limit_max = ChannelListHelper.get_channel_limit_range(
            merchant=merchant,
            payment_way=PayTypeEnum.WITHDRAW,
            client_ip=form.client_ip.data,
        )

        deposit_limit_config = dict(
            balance=user_balance.real_balance,
            limit_min=limit_min,
            limit_max=limit_max,
        )
        return ResponseWithdrawLimitConfig(bs_data=deposit_limit_config).as_response()


@ns.route('/banks/list', endpoint='withdraw_payment_type')
@ResponseDoc.response(ns, api)
class PaymentTypeList(Resource):
    method_decorators = cashier_decorators

    # 相应数据格式
    @ns.marshal_with(ResponseBankWithdraw.gen_doc(api))
    def post(self):
        """
        获取当前可用的充值方式
        """
        form, error = DomainForm().request_validate()
        if error:
            return error.as_response()

        channel_list = ChannelListHelper.get_available_channels(form.merchant.data, PayTypeEnum.WITHDRAW)
        withdraw_banks = []

        for channel in channel_list:
            banks = [dict(desc=bank.desc, value=bank.value) for bank in channel.banks]
            withdraw_banks += banks

        value_list = []
        banks_lst = []
        for item in withdraw_banks:
            if item['value'] not in value_list:
                value_list.append(item['value'])
                banks_lst.append(item)
        banks_result = dict(banks=banks_lst)
        return ResponseBankWithdraw(bs_data=banks_result).as_response()


@ns.route('/order/create')
@ResponseDoc.response(ns, api)
class WithdrawOrderCreate(Resource):
    method_decorators = cashier_decorators

    # 相应数据格式 前端传入用户 提现金额，用户所选的银行卡 标示号, 支付密码
    @ns.expect(WithdrawRequestDoc)
    @ns.marshal_with(ResponseSuccess.gen_doc(api))
    def post(self):
        """
        提现接口： 检查支付密码是否正确，如果密码正确则创建用户提现订单
        """
        form, error = CreateWithdrawOrderForm().request_validate()
        if error:
            return error.as_response()

        uid = g.user.uid
        merchant = g.user.merchant

        if not g.user.has_permission(UserPermissionEnum.WITHDRAW):
            return UserPermissionDeniedError().as_response()

        amount = BalanceKit.round_4down_5up(Decimal(form.amount.data))
        user_bank_id = form.user_bank.data
        client_ip = form.client_ip.data
        trade_password = form.trade_password.data

        # 判断 支付密码是否正确
        if not User.verify_payment_password(merchant=merchant, uid=uid, password=trade_password):
            cache = UserPaymentPasswordLimitCache(uid=uid)
            cache.incr_times()
            times = cache.get_left_times()
            return PaymentPasswordError(message=PaymentPasswordError.message.format(times)).as_response()

        order, error = WithdrawTransactionCtl.order_create(
            user=g.user,
            amount=amount,
            client_ip=client_ip,
            user_bank_id=user_bank_id,
        )
        if error:
            return error.as_response()

        return ResponseSuccess().as_response()
