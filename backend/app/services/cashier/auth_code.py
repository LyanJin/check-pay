import traceback

from flask import current_app
from flask_restplus import Resource

from app.extensions import limiter
from app.docs.doc_cashier.auth_code import MobileAuthCode, MobileNumber
from app.libs.error_code import ResponseSuccess, AccountAlreadyExitError, AuthCodeTimesLimitError, AuthCodeError, \
    AuthCodeExpiredError
from app.logics.mobile.auth_code import AuthCodeGenerator, AuthCodeLimiter
from app.libs.doc_response import ResponseDoc
from app.forms.auth_code import MobileRegisterCheckForm, AuthCodeForm
from app.extensions.ext_api import api_cashier as api

# 定义文档模型的名字空间
# 文档模型只是用来描述API，如API的请求/响应的数据格式
ns = api.namespace('sms', description='短信动态验证码API')


@ns.route('/get', endpoint='sms_get_code')
# 非200类型的响应模型，用response来装饰，可以装饰多个
@ResponseDoc.response(ns, api, [
    AuthCodeTimesLimitError, AccountAlreadyExitError
], login=False)
class SMSCodeGenerator(Resource):
    # 验证码的发送要限速
    method_decorators = [limiter.limit("1/10")]

    # 期待客户端请求的数据模型,使用expect来装饰
    @ns.expect(MobileNumber)
    # 给客户端返回的的响应数据模型，使用marshal_with来装饰
    @ns.marshal_with(ResponseSuccess.gen_doc(api))
    def post(self):
        """
        获取短信动态验证码
        """
        # 用户手机号格式验证
        form, error = MobileRegisterCheckForm().request_validate()
        if error:
            return error.as_response()

        # 首先获取当日是否已发送过验证码
        if AuthCodeLimiter(form.number.data).is_limited():
            return AuthCodeTimesLimitError().as_response()

        # 生成验证码
        code = AuthCodeGenerator(form.number.data).generate_code()

        # current_app.logger.info('code generated success, code: %s', code)

        # 将验证码以短信方式发送到用户手机
        try:
            if not current_app.config['DEBUG'] or current_app.config['TESTING']:
                from app.services.celery.sms import async_send_auth_code
                async_send_auth_code.delay(phone=form.number.data, code=code)
        except:
            current_app.config['SENTRY_DSN'] and current_app.logger.fatal(traceback.format_exc())

        # 验证码发送成功后，发送次数+1
        AuthCodeLimiter(form.number.data).incr_times()

        return ResponseSuccess().as_response()


@ns.route('/verify', endpoint='sms_verify_code')
# 非200类型的响应模型，用response来装饰，可以装饰多个
@ResponseDoc.response(ns, api, [
    AuthCodeError, AccountAlreadyExitError
], login=False)
class SMSCodeAuthentication(Resource):

    method_decorators = [limiter.limit("1/second"), ]

    # 期待客户端请求的数据模型,使用expect来装饰
    @ns.expect(MobileAuthCode)
    # 给客户端返回的的响应数据模型，使用marshal_with来装饰
    @ns.marshal_with(ResponseSuccess.gen_doc(api))
    def post(self):
        """
        验证短信动态验证码
        """
        # 验证表单手机号及验证码格式验证
        form, error = AuthCodeForm.request_validate()
        if error:
            return error.as_response()

        # 判断验证码是否过期
        if AuthCodeGenerator(form.number.data).is_expired(form.auth_code.data):
            return AuthCodeExpiredError().as_response()

        # 判断验证码是否正确
        if not AuthCodeGenerator(form.number.data).verify_code(form.auth_code.data):
            return AuthCodeError().as_response()

        return ResponseSuccess().as_response()
