"""
客户端注册和登录
"""
import traceback

from flask import current_app, g
from flask_restplus import Resource

from app.constants.cashier import SERVICE_URL
from app.docs.doc_cashier.auth_client import ClientAuthLogin, ResponseSuccessLogin
from app.docs.doc_cashier.auth_code import PassWordAuthCode, MobileNumber, MobileAuthCode, \
    ResetPassword, ResetPasswordVerify
from app.enums.account import AccountTypeEnum, AccountStateEnum
from app.enums.trade import PayTypeEnum
from app.extensions import limiter
from app.forms.auth_code import PasswordForm, MobileRegisterCheckForm, MobileRegisterTrueCheckForm, \
    PasswordTrueForm, AuthCodeTrueForm, ResetWordForm, ResetWordVerify
from app.forms.client_auth import LoginForm
from app.libs.doc_response import ResponseDoc
from app.libs.error_code import AuthCodeError, ResponseSuccess, \
    AccountAlreadyExitError, AccountNotExistError, LoginPasswordError, AuthCodeTimesLimitError, \
    RePasswordError, NoSourceError, PasswordError, AuthCodeExpiredError, OriPasswordError, DisableUserError, \
    MerchantConfigDepositError, MerchantConfigWithdrawError
from app.libs.string_kit import PhoneNumberParser
from app.logics.token.cashier_token import UserLoginToken, cashier_decorators
from app.logics.mobile.auth_code import AuthCodeGenerator, AuthCodeLimiter
from app.models.merchant import MerchantFeeConfig
from app.models.user import User, UserBindInfo
from app.extensions.ext_api import api_cashier as api
from app.caches.user_password import UserPasswordLimitCache

ns = api.namespace('auth', description='用户注册登录')


@ns.route('/mobile/check', endpoint="mobile_number_check")
@ResponseDoc.response(ns, api, [AccountAlreadyExitError], login=False)
class AuthUsername(Resource):
    method_decorators = [limiter.limit("1/second"), ]

    @ns.expect(MobileNumber)
    @ns.marshal_with(ResponseSuccess.gen_doc(api))
    def post(self):
        """
            检查手机号是否已经注册
        """
        form, error = MobileRegisterCheckForm().request_validate()
        if error:
            return error.as_response()

        if not MerchantFeeConfig.query_latest_one(query_fields=dict(
            merchant=form.merchant.data,
            payment_way=PayTypeEnum.DEPOSIT,
        )):
            return MerchantConfigDepositError().as_response()

        if not MerchantFeeConfig.query_latest_one(query_fields=dict(
            merchant=form.merchant.data,
            payment_way=PayTypeEnum.WITHDRAW,
        )):
            return MerchantConfigWithdrawError().as_response()

        return ResponseSuccess().as_response()


@ns.route('/account/register', endpoint='register')
@ResponseDoc.response(ns, api, [
    AuthCodeError, AccountAlreadyExitError
], login=False)
class UserRegisterAccount(Resource):
    method_decorators = [limiter.limit("1/second"), ]

    # 期待客户端请求数据模型， 用response 来装饰
    @ns.expect(PassWordAuthCode)
    @ns.marshal_with(ResponseSuccess.gen_doc(api))
    def post(self):
        """
        手机号码注册
        :return:
        """
        # 验证 手机号 验证码  密码格式
        form, error = PasswordForm().request_validate()
        if error:
            return error.as_response()

        # 判断验证码是否过期
        if AuthCodeGenerator(form.number.data).is_expired(form.auth_code.data):
            return AuthCodeExpiredError().as_response()

        # 判断验证码是否正确
        if not AuthCodeGenerator(form.number.data).verify_code(form.auth_code.data):
            return AuthCodeError().as_response()

        if not MerchantFeeConfig.query_latest_one(query_fields=dict(
            merchant=form.merchant.data,
            payment_way=PayTypeEnum.DEPOSIT,
        )):
            return MerchantConfigDepositError().as_response()

        if not MerchantFeeConfig.query_latest_one(query_fields=dict(
            merchant=form.merchant.data,
            payment_way=PayTypeEnum.WITHDRAW,
        )):
            return MerchantConfigWithdrawError().as_response()

        User.register_account(
            merchant=form.merchant.data,
            account=form.number.data,
            ac_type=AccountTypeEnum.MOBILE,
            login_pwd=form.password.data,
        )

        return ResponseSuccess().as_response()


@ns.route('/account/login', endpoint='get_token')
@ResponseDoc.response(ns, api, [AccountNotExistError, LoginPasswordError, DisableUserError, OriPasswordError],
                      login=False)
class ClientLogin(Resource):
    method_decorators = [limiter.limit("1/second"), ]

    @ns.expect(ClientAuthLogin)
    @ns.marshal_with(ResponseSuccessLogin.gen_doc(api))
    def post(self):
        """
        用户登陆获取token
        :return:
        """

        # 验证登陆表单是否正确
        form, error = LoginForm().request_validate()
        if error:
            return error.as_response()

        if not MerchantFeeConfig.query_latest_one(query_fields=dict(
            merchant=form.merchant.data,
            payment_way=PayTypeEnum.DEPOSIT,
        )):
            return MerchantConfigDepositError().as_response()

        if not MerchantFeeConfig.query_latest_one(query_fields=dict(
            merchant=form.merchant.data,
            payment_way=PayTypeEnum.WITHDRAW,
        )):
            return MerchantConfigWithdrawError().as_response()

        # 验证手机号是否已注册
        user_info = User.query_user(form.merchant.data, account=form.number.data)
        if not user_info:
            return AccountNotExistError().as_response()

        if user_info.state == AccountStateEnum.INACTIVE:
            return DisableUserError().as_response()

        # 验证用户名 密码是否正确
        if not User.verify_login(merchant=form.merchant.data, account=form.number.data, password=form.password.data):
            UserPasswordLimitCache(mobile_number=form.number.data).incr_times()

            # 获取密码输入错误次数是否达到上限
            if UserPasswordLimitCache(mobile_number=form.number.data).is_limited():
                User.update_user_state(form.merchant.data, account=form.number.data, state=AccountStateEnum.INACTIVE)
                return OriPasswordError().as_response()
            return LoginPasswordError().as_response()

        UserPasswordLimitCache(mobile_number=form.number.data).delete_cache()

        # 生成token 返回给客户端
        token = UserLoginToken.generate_token(uid=user_info.uid, merchant=form.merchant.data.value)

        # 显示用户名
        bind_info = UserBindInfo.query_bind_by_uid(user_info.uid)
        if bind_info:
            bind_name = bind_info.name
        else:
            bind_name = PhoneNumberParser.hide_number(user_info.account)

        return ResponseSuccessLogin(bs_data=dict(
            token=token,
            service_url=SERVICE_URL,
            permissions=user_info.permission_names,
            bind_name=bind_name,
            user_flag=user_info.flag.name,
        )).as_response()


# @ns.route('/account/delete', endpoint='delete_account')
# @ResponseDoc.response(ns, api, [AccountNotExistError, ])
# class DeleteAccount(Resource):
#     method_decorators = [limiter.limit("1/second"), ]
#
#     @ns.expect(MobileNumber)
#     @ns.marshal_with(ResponseSuccess.gen_doc(api))
#     def post(self):
#         """
#         删除账号
#         :return:
#         """
#         if not current_app.config['DEBUG']:
#             # 仅提供给测试环境使用
#             return Forbidden().as_response()
#
#         form, error = MobileNumberForm().request_validate()
#         if error:
#             return error.as_response()
#
#         user_info = User.query_user(form.merchant.data, account=form.number.data)
#         if not user_info:
#             return AccountNotExistError().as_response()
#
#         User.delete_account(form.merchant.data, account=form.number.data)
#
#         current_app.logger.info('delete user success, code: %s', form.number.data)
#
#         return ResponseSuccess().as_response()


@ns.route('/password/forget/get', endpoint='get_sms_auth')
@ResponseDoc.response(ns, api, [AccountNotExistError, AuthCodeTimesLimitError], login=False)
class ForgetPasswordGetAuth(Resource):
    method_decorators = [limiter.limit("1/10"), ]

    # 请求数据格式
    @ns.expect(MobileNumber)
    # 相应数据格式
    @ns.marshal_with(ResponseSuccess.gen_doc(api))
    def post(self):
        """
        忘记密码 --验证手机号，获取验证码
        :return:
        """
        # 用户手机号格式验证
        form, error = MobileRegisterTrueCheckForm().request_validate()
        if error:
            return error.as_response()

        # 首先获取当日是否已发送过验证码
        if AuthCodeLimiter(form.number.data).is_limited():
            return AuthCodeTimesLimitError().as_response()

        # 生成验证码
        code = AuthCodeGenerator(form.number.data).generate_code()

        current_app.logger.info('code generated success, code: %s', code)
        # print('code: %s' % code)

        # 将验证码以短信方式发送到用户手机
        try:
            if not current_app.config['DEBUG']:
                from app.services.celery.sms import async_send_auth_code
                async_send_auth_code.delay(phone=form.number.data, code=code)
        except:
            current_app.config['SENTRY_DSN'] and current_app.logger.fatal(traceback.format_exc())

        # 验证码发送成功后，发送次数+1
        AuthCodeLimiter(form.number.data).incr_times()

        return ResponseSuccess().as_response()


@ns.route('/password/forget/set', endpoint='forget_password_reset')
@ResponseDoc.response(ns, api, [AccountNotExistError, AuthCodeError], login=False)
class ForgetPasswordReset(Resource):
    method_decorators = [limiter.limit("1/second"), ]

    # 请求数据格式
    @ns.expect(PassWordAuthCode)
    # 相应数据格式
    @ns.marshal_with(ResponseSuccess.gen_doc(api))
    def post(self):
        """
        忘记密码 --设置新密码
        :return:
        """
        # 用户手机号格式验证
        form, error = PasswordTrueForm().request_validate()
        if error:
            return error.as_response()

        # 判断验证码是否过期
        if AuthCodeGenerator(form.number.data).is_expired(form.auth_code.data):
            return AuthCodeExpiredError().as_response()

        # 判断验证码是否正确
        if not AuthCodeGenerator(form.number.data).verify_code(form.auth_code.data):
            return AuthCodeError().as_response()

        User.reset_password(
            form.merchant.data,
            account=form.number.data,
            login_pwd=form.password.data
        )

        UserPasswordLimitCache(form.number.data).delete_cache()
        User.update_user_state(merchant=form.merchant.data, account=form.number.data, state=AccountStateEnum.ACTIVE)

        return ResponseSuccess().as_response()


@ns.route('/password/forget/verify', endpoint='verify_auth_code')
@ResponseDoc.response(ns, api, [AccountNotExistError, AuthCodeError], login=False)
class ForgetPasswordVerifyAuth(Resource):
    method_decorators = [limiter.limit("1/second"), ]

    # 请求数据格式
    @ns.expect(MobileAuthCode)
    # 相应数据格式
    @ns.marshal_with(ResponseSuccess.gen_doc(api))
    def post(self):
        """
        忘记密码 --验证验证码
        :return:
        """
        # 用户手机号格式验证
        form, error = AuthCodeTrueForm().request_validate()
        if error:
            return error.as_response()

        # 判断验证码是否过期
        if AuthCodeGenerator(form.number.data).is_expired(form.auth_code.data):
            return AuthCodeExpiredError().as_response()

        # 判断验证码是否正确
        if not AuthCodeGenerator(form.number.data).verify_code(form.auth_code.data):
            return AuthCodeError().as_response()

        return ResponseSuccess().as_response()


@ns.route('/password/reset', endpoint='reset_password')
@ResponseDoc.response(ns, api, [AccountNotExistError, RePasswordError, NoSourceError])
class ResetPassword(Resource):
    method_decorators = cashier_decorators

    # 请求数据格式
    @ns.expect(ResetPassword)
    # 相应数据格式
    @ns.marshal_with(ResponseSuccess.gen_doc(api))
    def post(self):
        """
        修改密码
        :return:
        """

        # 用户手机号格式验证
        form, error = ResetWordForm().request_validate()
        if error:
            return error.as_response()

        # 从全局变量中取出用户ID,参考：verify_credential
        uid = g.user.uid

        if not User.verify_password(merchant=form.merchant.data, uid=uid, password=form.ori_password.data):
            return PasswordError().as_response()

        if User.verify_password(merchant=form.merchant.data, uid=uid, password=form.new_password.data):
            return RePasswordError().as_response()

        flag = User.reset_password(
            form.merchant.data,
            uid=uid,
            login_pwd=form.new_password.data
        )
        if not flag:
            return NoSourceError().as_response()

        return ResponseSuccess().as_response()


@ns.route('/password/reset/verify', endpoint='reset_password_verify')
@ResponseDoc.response(ns, api, [AccountNotExistError, PasswordError, OriPasswordError])
class ResetPasswordVerify(Resource):
    method_decorators = cashier_decorators

    # 请求数据格式
    @ns.expect(ResetPasswordVerify)
    # 相应数据格式
    @ns.marshal_with(ResponseSuccess.gen_doc(api))
    def post(self):
        """
        修改密码  验证原始密码是否正确
        :return:
        """

        # 用户手机号格式验证
        form, error = ResetWordVerify().request_validate()
        if error:
            return error.as_response()

        # 获取用户信息
        user = g.user

        # 判断当前用户状态是否为 INACTIVE 如果是则返回错误信息
        if not user.is_active:
            return DisableUserError().as_response()

        # 验证原始密码是否正确
        if not User.verify_password(merchant=form.merchant.data, uid=user.uid, password=form.ori_password.data):
            # 密码输入错误 则将密码输入错误次数 + 1 返回密码有误 信息
            UserPasswordLimitCache(user.account).incr_times()

            # 判断用户当天密码错误次数是否达到上限 如果达到上限 更改账户状态 返回错误
            if UserPasswordLimitCache(user.account).is_limited():
                User.update_user_state(user.merchant, account=user.account, state=AccountStateEnum.INACTIVE)
                return OriPasswordError().as_response()

            return PasswordError().as_response()

        # 如果密码输入次数未达上限 且密码验证成功则删除缓存数据
        UserPasswordLimitCache(user.account).delete_cache()

        return ResponseSuccess().as_response()
