# -*-coding:utf8-*-
from flask import g

from app.constants.trade import TRANSFER_AMOUNT_LIMIT
from app.docs.doc_cashier.user_info import ResponseTransferUserQueryResult
from app.enums.account import AccountTypeEnum, UserPermissionEnum
from app.extensions.ext_api import api_cashier as api
from flask_restplus import Resource
from app.libs.doc_response import ResponseDoc
from app.libs.string_kit import PhoneNumberParser
from app.logics.token.cashier_token import cashier_decorators
from app.libs.error_code import ResponseSuccess, PaymentPwdNotExistError, NoSourceError, PaymentPasswordError, \
    PaymentPasswordLimitedError, AccountNotExistError, AccountBalanceInsufficientError, TransferToMeError, \
    UserPermissionDeniedError
from app.forms.auth_code import TransferForm, TransferAccountQueryForm
from app.docs.doc_cashier.auth_code import TransferParam, TransferAccountQueryDoc
from app.caches.user_payment_password import UserPaymentPasswordLimitCache
from app.models.user import User, UserBindInfo
from app.models.balance import UserBalance, UserBalanceEvent
from app.libs.balance_kit import BalanceKit


ns = api.namespace('transfer', description='转账')


@ns.route('/account/query')
@ResponseDoc.response(ns, api, [
    AccountNotExistError
])
class QueryTransferAccount(Resource):
    method_decorators = cashier_decorators

    @ns.expect(TransferAccountQueryDoc)
    @ns.marshal_with(ResponseTransferUserQueryResult.gen_doc(api))
    def post(self):
        form, error = TransferAccountQueryForm().request_validate()
        if error:
            return error.as_response()

        bind_user = UserBindInfo.query_bind(form.merchant.data, form.account.data)
        if not bind_user:
            # 未绑定账号，验证手机号码是否正确
            account = form.join_phone_number()
            if not account:
                return AccountNotExistError(message="您输入的账号不存在").as_response()
            form.account.data = account
        else:
            # 使用绑定的手机号码
            form.account.data = bind_user.account

        user_info = User.query_user(form.merchant.data, account=form.account.data)
        if not user_info:
            return AccountNotExistError(message="您输入的账号未注册").as_response()

        no_transfer_limit = UserBindInfo.query_bind_by_uid(user_info.uid)

        return ResponseTransferUserQueryResult(bs_data=dict(
            is_auth=user_info.is_official_auth,
            transfer_limit=0 if no_transfer_limit else TRANSFER_AMOUNT_LIMIT,
        )).as_response()


@ns.route('/transfer')
@ResponseDoc.response(ns, api, [
    AccountBalanceInsufficientError, PaymentPasswordError, PaymentPwdNotExistError, PaymentPasswordLimitedError, 
    TransferToMeError, AccountNotExistError, UserPermissionDeniedError
])
class Transfer(Resource):
    method_decorators = cashier_decorators

    # 期待客户端请求数据模型， 用response 来装饰
    @ns.expect(TransferParam)
    # 相应数据格式
    @ns.marshal_with(ResponseSuccess.gen_doc(api))
    def post(self):
        """
        转账
        判断接受转账的用户是否存在
        判断是否存在支付密码
        校验老的支付密码
        判断余额是否足够
        执行转账操作
        """

        form, error = TransferForm().request_validate()
        if error:
            return error.as_response()

        # 从全局变量中取出用户ID,参考：verify_credential
        uid = g.user.uid

        if not g.user.has_permission(UserPermissionEnum.TRANSFER):
            return UserPermissionDeniedError().as_response()

        # 判断接受转账的用户是否存在
        bind_user = UserBindInfo.query_bind(form.merchant.data, form.number.data)
        if not bind_user:
            # 未绑定账号，验证手机号码是否正确
            account = form.join_phone_number()
            if not account:
                return AccountNotExistError(message="您输入的账号不存在").as_response()
            form.number.data = account
        else:
            # 使用绑定的手机号码
            form.number.data = bind_user.account

        user_info = User.query_user(form.merchant.data, account=form.number.data)
        if not user_info:
            return AccountNotExistError(message="账号(%s)不存在" % form.number.data).as_response()

        no_transfer_limit = UserBindInfo.query_bind_by_uid(user_info.uid)
        if not no_transfer_limit and form.amount.data > TRANSFER_AMOUNT_LIMIT:
            # 非绑定用户转账限额检查
            return UserPermissionDeniedError(message="单次转账额度不能超过%s" % TRANSFER_AMOUNT_LIMIT).as_response()

        # 判断是否是给自己转账
        if uid == user_info.uid:
            return TransferToMeError().as_response()

        # 判断是否存在支付密码
        user = User.query_user(form.merchant.data, uid)

        if not user.trade_pwd:
            return PaymentPwdNotExistError().as_response()

        cache = UserPaymentPasswordLimitCache(uid=uid)

        # 获取支付密码输入错误次数是否达到上限
        if cache.is_limited():
            return PaymentPasswordLimitedError().as_response()

        # 校验支付密码
        flag = User.verify_payment_password(
            form.merchant.data,
            uid=uid,
            password=form.payment_password.data
        )

        # 交易密码校验失败
        if not flag:
            cache.incr_times()
            times = cache.get_left_times()
            return PaymentPasswordError(message=PaymentPasswordError.message.format(times)).as_response()

        # 密码校验成功 删除密码输入错误记录
        cache.delete_cache()

        # 判断余额是否足够
        balance = UserBalance.query_balance(
            uid=uid, merchant=g.user.merchant).first()
        if BalanceKit.divide_unit(balance.balance) < form.amount.data:
            return AccountBalanceInsufficientError().as_response()

        # 执行转账动作
        flag, msg = UserBalanceEvent.transfer(
            from_user=g.user,
            to_user=user_info,
            merchant=form.merchant.data,
            amount=form.amount.data,
            comment=form.comment.data
        )

        # 设置失败的情况
        if not flag:
            return NoSourceError().as_response()

        return ResponseSuccess().as_response()
