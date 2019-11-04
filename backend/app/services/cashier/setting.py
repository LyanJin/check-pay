# -*-coding:utf8-*-
from flask import g

from app.enums.account import UserPermissionEnum
from app.enums.trade import PaymentBankEnum
from app.extensions.ext_api import api_cashier as api
from flask_restplus import Resource
from app.libs.doc_response import ResponseDoc
from app.logics.token.cashier_token import cashier_decorators
from app.libs.error_code import AuthCodeError, ResponseSuccess, \
    BankCardNotExistError, BankCardNotMeError, PaymentPwdNotExistError, NoSourceError, PaymentPasswordError, \
    PaymentPasswordLimitedError, PaymentPwdResetSameError, AuthCodeExpiredError, InvalidBankNumber, \
    BankCardNumLimitedError, BankCardAccountNameError, BankCardExistError, UserPermissionDeniedError
from app.forms.auth_code import SetPaymentPassword, ResetPaymentPasswordForm, \
    SetForgetPaymentPasswordForm, BankCardForm, CreateBankCardForm, \
    DeleteBankCardForm
from app.docs.doc_cashier.auth_code import PaymentPassword, ResetPaymentPassword, SetForgetPaymentPassword, \
    ResponsePaymentPasswordRemaintimes, \
    ResponseBanks, BankCardId, ResponseBankLocation, BankCardParams, ResponseBankCards, BankCardDeleteParams
from app.models.user import User
from app.caches.user_payment_password import UserPaymentPasswordLimitCache
from app.logics.mobile.auth_code import AuthCodeGenerator
from app.constants.trade import USER_BANK_CARD_NUM_LIMIT
from app.models.bank import Bank
from app.models.bankcard import BankCard
from app.libs.yonyou.bank import BankToolKit

ns = api.namespace('setting', description='用户设置')


@ns.route('/payment/password/set', endpoint='set_payment_password')
@ResponseDoc.response(ns, api, [PaymentPwdNotExistError, NoSourceError])
class PaymentPasswordSet(Resource):
    method_decorators = cashier_decorators

    # 期待客户端请求数据模型， 用response 来装饰
    @ns.expect(PaymentPassword)
    # 相应数据格式
    @ns.marshal_with(ResponseSuccess.gen_doc(api))
    def post(self):
        """
        设置支付密码
        """

        """
        判断密码是否是6位纯数字
        判断密码是否是连续的
        判断是否存在支付密码
        写入支付密码到数据库
        """

        form, error = SetPaymentPassword().request_validate()
        if error:
            return error.as_response()

        # 从全局变量中取出用户ID,参考：verify_credential
        uid = g.user.uid

        # 判断是否存在支付密码
        user = User.query_user(form.merchant.data, uid)

        if user.trade_pwd:
            return PaymentPwdNotExistError().as_response()

        # 设置支付密码
        flag = User.set_payment_password(
            form.merchant.data,
            uid=uid,
            trade_pwd=form.payment_password.data
        )

        # 设置失败的情况
        if not flag:
            return NoSourceError().as_response()

        return ResponseSuccess().as_response()


@ns.route('/payment/password/check', endpoint='check_payment_password')
@ResponseDoc.response(ns, api, [PaymentPwdNotExistError, PaymentPasswordError])
class PaymentPasswordCheck(Resource):
    method_decorators = cashier_decorators

    # 期待客户端请求数据模型， 用response 来装饰
    @ns.expect(PaymentPassword)
    # 相应数据格式
    @ns.marshal_with(ResponseSuccess.gen_doc(api))
    def post(self):
        """
        校验支付密码
        """

        """
        判断是否设置了支付密码
        校验支付密码
        """

        form, error = SetPaymentPassword().request_validate()
        if error:
            return error.as_response()

        # 从全局变量中取出用户ID,参考：verify_credential
        uid = g.user.uid

        # 判断是否存在支付密码
        user = User.query_user(form.merchant.data, uid)

        if not user.trade_pwd:
            return PaymentPwdNotExistError().as_response()

        cache = UserPaymentPasswordLimitCache(uid=uid)
        # 获取支付密码输入错误次数是否达到上限
        if cache.is_limited():
            return PaymentPasswordLimitedError().as_response()

        flag = User.verify_payment_password(
            form.merchant.data,
            uid=uid,
            password=form.payment_password.data
        )

        # 交易密码校验失败
        if not flag:
            cache.incr_times()
            times = cache.get_left_times()
            # 获取支付密码输入错误次数是否达到上限（多判断一次 防止出现剩余0次的情况）
            if cache.is_limited():
                return PaymentPasswordLimitedError().as_response()
            return PaymentPasswordError(message=PaymentPasswordError.message.format(times)).as_response()

        # 密码校验成功 删除密码输入错误记录
        cache.delete_cache()

        return ResponseSuccess().as_response()


@ns.route('/payment/password/reset', endpoint='reset_payment_password')
@ResponseDoc.response(ns, api)
class PaymentPasswordReset(Resource):
    method_decorators = cashier_decorators

    # 期待客户端请求数据模型， 用response 来装饰
    @ns.expect(ResetPaymentPassword)
    # 相应数据格式
    @ns.marshal_with(ResponseSuccess.gen_doc(api))
    def post(self):
        """
        修改支付密码
        """

        """
        判断两次的密码是否相同
        判断是否存在支付密码
        校验老的支付密码
        设置新的支付密码
        """

        form, error = ResetPaymentPasswordForm().request_validate()
        if error:
            return error.as_response()

        # 判断两次的密码是否相同
        if form.ori_payment_password.data == form.new_payment_password.data:
            return PaymentPwdResetSameError().as_response()

        # 从全局变量中取出用户ID,参考：verify_credential
        uid = g.user.uid

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
            password=form.ori_payment_password.data
        )

        # 交易密码校验失败
        if not flag:
            cache.incr_times()
            times = cache.get_left_times()
            return PaymentPasswordError(message=PaymentPasswordError.message.format(times)).as_response()

        # 密码校验成功 删除密码输入错误记录
        cache.delete_cache()

        # 设置新的支付密码
        flag = User.set_payment_password(
            form.merchant.data,
            uid=uid,
            trade_pwd=form.new_payment_password.data
        )

        # 设置失败的情况
        if not flag:
            return NoSourceError().as_response()

        return ResponseSuccess().as_response()


@ns.route('/payment/password/forget/set', endpoint='set_forget_payment_password')
@ResponseDoc.response(ns, api, [AuthCodeExpiredError, AuthCodeError, PaymentPwdNotExistError, NoSourceError])
class PaymentPasswordForgetSet(Resource):
    method_decorators = cashier_decorators

    # 期待客户端请求数据模型， 用response 来装饰
    @ns.expect(SetForgetPaymentPassword)
    # 相应数据格式
    @ns.marshal_with(ResponseSuccess.gen_doc(api))
    def post(self):
        """
        忘记支付密码，重置支付密码
        """

        """
        检查验证码
        判断是否存在支付密码
        设置新的支付密码
        """

        form, error = SetForgetPaymentPasswordForm().request_validate()
        if error:
            return error.as_response()

        # 判断验证码是否过期
        if AuthCodeGenerator(form.number.data).is_expired(form.auth_code.data):
            return AuthCodeExpiredError().as_response()

        # 判断验证码是否正确
        if not AuthCodeGenerator(form.number.data).verify_code(form.auth_code.data):
            return AuthCodeError().as_response()

        # 从全局变量中取出用户ID,参考：verify_credential
        uid = g.user.uid

        # 判断是否存在支付密码
        user = User.query_user(form.merchant.data, uid)

        if not user.trade_pwd:
            return PaymentPwdNotExistError().as_response()

        # 设置新的支付密码
        flag = User.set_payment_password(
            form.merchant.data,
            uid=uid,
            trade_pwd=form.new_payment_password.data
        )

        # 设置失败的情况
        if not flag:
            return NoSourceError().as_response()

        try:
            # 清理掉支付密码输入错误的次数记录
            cache = UserPaymentPasswordLimitCache(uid=uid)

            # 密码设置成功 删除密码输入错误记录
            cache.delete_cache()
        except:
            pass

        return ResponseSuccess().as_response()


@ns.route('/payment/password/remaintimes/get', endpoint='get_payment_password_remaintimes')
@ResponseDoc.response(ns, api)
class PaymentPasswordRemaintimes(Resource):
    method_decorators = cashier_decorators

    # 相应数据格式
    @ns.marshal_with(ResponsePaymentPasswordRemaintimes.gen_doc(api))
    def post(self):
        """
        获取支付密码剩余可输入次数
        """

        # 从全局变量中取出用户ID,参考：verify_credential
        uid = g.user.uid

        # 获取今日输入错误支付密码的次数
        left_times = UserPaymentPasswordLimitCache(uid=uid).get_left_times()

        return ResponsePaymentPasswordRemaintimes(bs_data=dict(times=left_times)).as_response()


@ns.route('/bank/list', endpoint='get_banks')
@ResponseDoc.response(ns, api)
class GetBankList(Resource):
    # 相应数据格式
    @ns.marshal_with(ResponseBanks.gen_doc(api))
    def post(self):
        """
        获取银行列表
        """

        # 获取所有的银行卡列表数据
        bank_list = Bank.query_all()

        # 构造返回的数据字典
        bank_dict = dict(banks=[dict(
            bank_name=item.bank_name,
            bank_code=item.bank_code) for item in bank_list])

        # 返回json数据到前端
        return ResponseBanks(bs_data=bank_dict).as_response()


@ns.route('/bank/banklocation/get', endpoint='get_bank_location')
@ResponseDoc.response(ns, api, [InvalidBankNumber])
class GetBankLocation(Resource):

    # 期待客户端请求数据模型， 用response 来装饰
    @ns.expect(BankCardId)
    # 相应数据格式
    @ns.marshal_with(ResponseBankLocation.gen_doc(api))
    def post(self):
        """
        根据卡号获取银行卡归属地信息
        """

        form, error = BankCardForm().request_validate()
        if error:
            return error.as_response()

        # 根据接口获取银行卡归属地信息
        bank_location = BankToolKit().get_bank_location(form.card_id.data)

        # 判断是否接口调用成功
        if bank_location.get('error_code') != 0:
            return InvalidBankNumber(message=bank_location['reason']).as_response()

        # 返回json数据到前端
        return ResponseBankLocation(bs_data=dict(province=bank_location['result']['province'],
                                                 city=bank_location['result']['city'],
                                                 bank_code=bank_location['result']['abbreviation'],
                                                 bank_name=bank_location['result']['bankname'])).as_response()


@ns.route('/bankcard/list', endpoint='get_bankcards')
@ResponseDoc.response(ns, api)
class GetBankCardList(Resource):
    method_decorators = cashier_decorators

    # 相应数据格式
    @ns.marshal_with(ResponseBankCards.gen_doc(api))
    def post(self):
        """
        获取用户的银行卡列表
        """

        # 从全局变量中取出用户ID,参考：verify_credential
        uid = g.user.uid
        merchant = g.user.merchant

        # 获取所有的银行卡列表数据
        bank_card_list = BankCard.query_bankcards_by_uid(merchant, uid)

        print(bank_card_list)

        # 构造返回的数据字典
        bank_card_dict = dict(bankcards=[dict(
            id=item.id,
            bank_name=item.bank_name,
            bank_code=item.bank_code,
            account_name=item.account_name,
            bank_idx=PaymentBankEnum.get_bank_by_code(item.bank_code).value,
            card_no="**** **** **** " + item.card_no[-4:],
        ) for item in bank_card_list])

        # 返回json数据到前端
        return ResponseBankCards(bs_data=bank_card_dict).as_response()


@ns.route('/bankcard/add', endpoint='add_bankcard')
@ResponseDoc.response(ns, api, [
    PaymentPasswordLimitedError, PaymentPasswordError, BankCardNumLimitedError, BankCardAccountNameError,
    BankCardExistError, UserPermissionDeniedError
])
class BankCardAdd(Resource):
    method_decorators = cashier_decorators

    # 期待客户端请求数据模型， 用response 来装饰
    @ns.expect(BankCardParams)
    # 相应数据格式
    @ns.marshal_with(ResponseSuccess.gen_doc(api))
    def post(self):
        """
        给用户添加银行卡
        """

        """
        判断是否达到了8张银行卡的限制
        读取用户之前的银行卡信息
        如果存在需要判断开户人跟之前的一致
        判断卡号是否已经存在了
        写入数据库
        """

        form, error = CreateBankCardForm().request_validate()
        if error:
            return error.as_response()

        # 从全局变量中取出用户ID,参考：verify_credential
        uid = g.user.uid
        merchant = g.user.merchant

        if not g.user.has_permission(UserPermissionEnum.BINDCARD):
            return UserPermissionDeniedError().as_response()

        # 获取支付密码输入错误次数是否达到上限
        if UserPaymentPasswordLimitCache(uid=uid).is_limited():
            return PaymentPasswordLimitedError().as_response()

        # 校验支付密码
        flag = User.verify_payment_password(
            form.merchant.data,
            uid=uid,
            password=form.payment_password.data
        )

        # 交易密码校验失败
        if not flag:
            UserPaymentPasswordLimitCache(uid=uid).incr_times()
            return PaymentPasswordError().as_response()

        # 密码校验成功 删除密码输入错误记录
        UserPaymentPasswordLimitCache(uid=uid).delete_cache()

        # 判断是否达到了8张银行卡的限制
        bank_card_list = BankCard.query_bankcards_by_uid(merchant, uid)
        bank_card_num = len(bank_card_list)
        if bank_card_num > USER_BANK_CARD_NUM_LIMIT:
            return BankCardNumLimitedError().as_response()

        account_name = form.account_name.data
        # 如果存在需要判断开户人跟之前的一致
        if bank_card_num > 0:
            account_name = bank_card_list[0]['account_name']

        if account_name != form.account_name.data:
            return BankCardAccountNameError().as_response()

        # 判断卡号是否已经存在了
        bank_card_info = BankCard.query_bankcard_by_card_no(
            merchant, form.card_no.data)
        if bank_card_info is not None:
            return BankCardExistError().as_response()

        # 写入数据库
        flag = BankCard.add_bank_card(
            merchant,
            uid=uid,
            bank_name=form.bank_name.data,
            bank_code=form.bank_code.data,
            card_no=form.card_no.data,
            account_name=form.account_name.data,
            branch=form.branch.data,
            province=form.province.data,
            city=form.city.data,
        )

        # 设置失败的情况
        if not flag:
            return NoSourceError().as_response()

        return ResponseSuccess().as_response()


@ns.route('/bankcard/delete', endpoint='delete_bankcard')
@ResponseDoc.response(ns, api, [
    PaymentPasswordLimitedError, PaymentPasswordError, BankCardNotExistError, BankCardNotMeError,
])
class BankCardDelete(Resource):
    method_decorators = cashier_decorators

    # 期待客户端请求数据模型， 用response 来装饰
    @ns.expect(BankCardDeleteParams)
    # 相应数据格式
    @ns.marshal_with(ResponseSuccess.gen_doc(api))
    def post(self):
        """
        删除用户银行卡
        """

        """
        校验老的支付密码
        删除银行卡
        """

        form, error = DeleteBankCardForm().request_validate()
        if error:
            return error.as_response()

        # 从全局变量中取出用户ID,参考：verify_credential
        uid = g.user.uid

        # 获取支付密码输入错误次数是否达到上限
        if UserPaymentPasswordLimitCache(uid=uid).is_limited():
            return PaymentPasswordLimitedError().as_response()

        # 校验支付密码
        flag = User.verify_payment_password(
            form.merchant.data,
            uid=uid,
            password=form.payment_password.data
        )

        # 交易密码校验失败
        if not flag:
            UserPaymentPasswordLimitCache(uid=uid).incr_times()
            return PaymentPasswordError().as_response()

        # 密码校验成功 删除密码输入错误记录
        UserPaymentPasswordLimitCache(uid=uid).delete_cache()

        # 查询银行卡信息
        bank_card = BankCard.query_bankcard_by_id(form.bank_card_id.data)
        if bank_card is None:
            return BankCardNotExistError().as_response()

        if uid != bank_card.uid:
            return BankCardNotMeError().as_response()

        BankCard.delete_bankcard_by_card_no(
            form.merchant.data,
            card_no=bank_card.card_no
        )

        return ResponseSuccess().as_response()
