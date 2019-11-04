"""
使用basic auth进行token鉴权
客户端浏览器使用sessionStorage来存储token，用户关闭浏览器及token失效，需要重新登录
"""
from flask import g
from flask_httpauth import HTTPTokenAuth

from app.constants.admin_ip import ADMIN_IP_WHITE_LIST
from app.extensions import limiter
from app.libs.api_exception import APIException
from app.libs.error_code import DisableUserError, AccountNotExistError
from app.libs.decorators import check_ip_in_white_list
from app.logics.token.token_base import AdminLoginToken
from app.models.backoffice.admin_user import AdminUser

admin_auth = HTTPTokenAuth(scheme='Bearer')


@admin_auth.error_handler
def handle_token_auth_error():
    if isinstance(g.error, APIException):
        return g.error.as_json_response()
    return "Unauthorized Access"


@admin_auth.verify_token
def verify_credential(token):
    """
    使用basic auth进行JWT token鉴权
    加了装饰器 @auth.login_required 的view都需要先进这个函数进行token鉴权
    :param token:
    :return:
    """

    # 初始化g对象的error属性
    g.error = None

    rst = AdminLoginToken.verify_token(token)
    if isinstance(rst, (APIException,)):
        # token 验证失败
        g.error = rst
        return False

    # 账户被封处理
    user = AdminUser.query_user(uid=rst['uid'])
    if not user:
        # 用户不存在
        g.error = AccountNotExistError()
        return False

    if not user.is_active:
        g.error = DisableUserError()
        return False

    g.user = user
    return True


# admin的装饰器
def get_admin_decorators(ip_check=True, limit_cond="1/second", auth=True):
    decs = []
    if ip_check:
        decs.append(check_ip_in_white_list(ADMIN_IP_WHITE_LIST))
    if limit_cond:
        decs.append(limiter.limit(limit_cond))
    if auth:
        decs.append(admin_auth.login_required)
    return decs


admin_decorators = get_admin_decorators()
