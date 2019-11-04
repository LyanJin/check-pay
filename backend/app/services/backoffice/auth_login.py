from flask import g
from flask_restplus import Resource

from app.constants.admin_ip import ADMIN_IP_WHITE_LIST
from app.docs.doc_internal.auth_login import AdminAccountLogin, AdminLoginResponse, AdminResetPassword
from app.extensions import limiter
from app.extensions.ext_api import api_backoffice as api
from app.libs.decorators import check_ip_in_white_list
from app.libs.doc_response import ResponseDoc
from app.libs.error_code import ResponseSuccess, LoginPasswordError, LoginAccountError, PasswordError, RePasswordError, \
    NoSourceError
from app.logics.token.admin_token import admin_decorators
from app.logics.token.token_base import AdminLoginToken
from app.models.backoffice.admin_user import AdminUser
from app.forms.backoffice.auth_login import AuthLoginForm, ResetWordForm

ns = api.namespace('auth', description='用户登录')

DEBUG_LOG = False


# @ns.route('/account/register', endpoint='admin_account_register')
# @ResponseDoc.response(ns, api, [LoginPasswordError, LoginAccountError])
# class ClientRegister(Resource):
#
#     @ns.expect(AdminAccountRegister)
#     @ns.marshal_with(AdminRegisterResponse.gen_doc(api))
#     def post(self):
#         """
#         测试环境注册账号
#         :return:
#         """
#
#         if not (current_app.config['DEBUG'] or current_app.config['TESTING']):
#             # 目前仅仅支持测试环境调试使用
#             raise
#
#         form, error = AdminTestRegisterForm.request_validate()
#         if error:
#             return error.as_response()
#
#         md5_password = hashlib.md5(form.password.data.encode('utf8')).hexdigest()
#         AdminUser.register_account(account=form.account.data, login_pwd=md5_password)
#
#         return AdminRegisterResponse(bs_data=dict(
#             md5_password=md5_password,
#         )).as_response()


@ns.route('/account/login', endpoint='admin_account_login')
@ResponseDoc.response(ns, api, [LoginPasswordError, LoginAccountError])
class ClientLogin(Resource):
    method_decorators = [check_ip_in_white_list(ADMIN_IP_WHITE_LIST), limiter.limit("1/second")]

    @ns.expect(AdminAccountLogin)
    @ns.marshal_with(AdminLoginResponse.gen_doc(api))
    def post(self):
        """
        后台用户登录
        :return:
        """
        form, error = AuthLoginForm.request_validate()
        if error:
            return error.as_response()

        user = AdminUser.query_user(account=form.account.data)
        if not user:
            return LoginAccountError().as_response()

        # 验证用户名密码是否正确
        if not AdminUser.verify_login(account=form.account.data, password=form.password.data):
            return LoginPasswordError().as_response()

        # 验证成功后，调用login_user，会在session中记录已经登录
        user = AdminUser.query_user(account=form.account.data)

        # 记录登录状态
        token = AdminLoginToken.generate_token(user.uid)

        # current_app.logger.debug('login ok, path: %s', request.path)

        return AdminLoginResponse(bs_data=dict(token=token)).as_response()


@ns.route('/account/logout', endpoint='admin_account_logout')
@ResponseDoc.response(ns, api)
class ClientLogout(Resource):
    method_decorators = admin_decorators

    @ns.marshal_with(ResponseSuccess.gen_doc(api))
    def post(self):
        """
        后台用户登出
        :return:
        """
        # current_app.logger.debug('logout, path: %s, uid: %s', request.path, g.user.uid)

        # 记录登录状态
        AdminLoginToken.remove_token(g.user.uid)

        return ResponseSuccess().as_response()


@ns.route('/password/reset', endpoint='reset_password')
@ResponseDoc.response(ns, api)
class ResetPassword(Resource):
    method_decorators = admin_decorators

    # 请求数据格式
    @ns.expect(AdminResetPassword)
    # 相应数据格式
    @ns.marshal_with(ResponseSuccess.gen_doc(api))
    def post(self):
        """
        修改登录密码
        :return:
        """
        # 格式验证
        form, error = ResetWordForm().request_validate()
        if error:
            return error.as_response()

        # 获取用户ID
        uid = g.user.uid

        if not AdminUser.verify_password(uid=uid, password=form.ori_password.data):
            return PasswordError().as_response()

        if AdminUser.verify_password(uid=uid, password=form.new_password.data):
            return RePasswordError().as_response()

        flag = AdminUser.reset_password(
            uid=uid,
            login_pwd=form.new_password.data
        )
        if not flag:
            return NoSourceError().as_response()

        return ResponseSuccess().as_response()
