from app.constants.admin_ip import MERCHANT_ADMIN_IP_LIST
from app.docs.doc_merchantoffice.auth_login import AdminMerchantLogin, MerchantLoginResponse, MerchantRegister
from app.extensions import limiter
from app.libs.decorators import check_ip_in_white_list
from . import api
from app.forms.merchantoffice.auth_login import MerchantLoginForm
from flask import g
from app.libs.doc_response import ResponseDoc
from flask_restplus import Resource

from app.libs.error_code import MerchantLoginAccountError, MerchantLoginPasswordError, ResponseSuccess
from app.logics.token.merchant_token import merchant_decorators
from app.logics.token.token_base import MerchantLoginToken
from app.models.merchantoffice.merchant_user import MerchantUser

ns = api.namespace('auth', description='商户登录')


@ns.route('/merchant/login', endpoint='merchant_account_login')
@ResponseDoc.response(ns, api, [MerchantLoginPasswordError, MerchantLoginAccountError])
class ClientLogin(Resource):
    method_decorators = [check_ip_in_white_list(MERCHANT_ADMIN_IP_LIST), limiter.limit("1/second")]

    @ns.expect(AdminMerchantLogin)
    @ns.marshal_with(MerchantLoginResponse.gen_doc(api))
    def post(self):
        """
        商户后台 登录
        :return:
        """
        form, error = MerchantLoginForm.request_validate()
        if error:
            return error.as_response()

        merchant_enum = form.account.data
        user = MerchantUser.query_user(account=merchant_enum.name)
        if not user:
            return MerchantLoginAccountError().as_response()

        # 验证用户名密码是否正确
        if not MerchantUser.verify_login(account=merchant_enum.name, password=form.password.data):
            return MerchantLoginPasswordError().as_response()

        # 验证成功后，调用login_user，会在session中记录已经登录
        user = MerchantUser.query_user(account=merchant_enum.name)

        # 记录登录状态
        token = MerchantLoginToken.generate_token(user.mid)

        # current_app.logger.debug('login ok, path: %s', request.path)

        return MerchantLoginResponse(bs_data=dict(token=token)).as_response()


@ns.route('/merchant/logout', endpoint='merchant_account_logout')
@ResponseDoc.response(ns, api)
class ClientLogout(Resource):
    method_decorators = merchant_decorators

    @ns.marshal_with(ResponseSuccess.gen_doc(api))
    def post(self):
        """
        商户后台 登出
        :return:
        """
        # current_app.logger.debug('logout, path: %s, uid: %s', request.path, g.user.uid)

        # 记录登录状态
        MerchantLoginToken.remove_token(g.user.mid)

        return ResponseSuccess().as_response()


@ns.route('/merchant/register', endpoint='merchant_account_register')
@ResponseDoc.response(ns, api)
class ClientRegister(Resource):
    method_decorators = [check_ip_in_white_list(MERCHANT_ADMIN_IP_LIST), limiter.limit("1/second")]

    @ns.expect(MerchantRegister)
    @ns.marshal_with(ResponseSuccess.gen_doc(api))
    def post(self):
        """
        商户后台 注册
        """
        form, error = MerchantLoginForm().request_validate()
        if error:
            return error.as_response()

        merchant_enum = form.account.data
        user = MerchantUser.register_account(mid=merchant_enum.value, account=merchant_enum.name,
                                             password=form.password.data)
        if user:
            return ResponseSuccess().as_response()
