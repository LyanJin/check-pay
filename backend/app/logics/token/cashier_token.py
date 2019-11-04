"""
使用basic auth进行token鉴权
客户端浏览器使用sessionStorage来存储token，用户关闭浏览器及token失效，需要重新登录
"""
from flask import g
from flask_httpauth import HTTPTokenAuth

from app.extensions import limiter
from app.libs.api_exception import APIException
from app.libs.error_code import DisableUserError, AccountNotExistError
from app.logics.token.token_base import UserLoginToken
from app.models.user import User
from config import MerchantEnum

cashier_auth = HTTPTokenAuth(scheme='Bearer')


@cashier_auth.error_handler
def handle_token_auth_error():
    if isinstance(g.error, APIException):
        return g.error.as_json_response()
    return "Unauthorized Access"


@cashier_auth.verify_token
def verify_credential(token):
    """
    使用basic auth进行JWT token鉴权
    加了装饰器 @auth.login_required 的view都需要先进这个函数进行token鉴权
    :param token:
    :return:
    """

    # 初始化g对象的error属性
    g.error = None

    rst = UserLoginToken.verify_token(token)
    if isinstance(rst, (APIException,)):
        # token 验证失败
        g.error = rst
        return False

    # 账户被封处理
    merchant = MerchantEnum(rst['merchant'])
    user = User.query_user(merchant=merchant, uid=rst['uid'])
    if not user:
        # 用户不存在
        g.error = AccountNotExistError()
        return False

    if not user.is_active:
        g.error = DisableUserError()
        return False

    g.user = user
    return True


# 登录后的钱包接口频率限制
def get_cashier_decorators(limit_cond="1/second", auth=True):
    decs = []
    if limit_cond:
        decs.append(limiter.limit(limit_cond))
    if auth:
        decs.append(cashier_auth.login_required)
    return decs


cashier_decorators = get_cashier_decorators()
