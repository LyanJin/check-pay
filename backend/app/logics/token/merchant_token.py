from flask_httpauth import HTTPTokenAuth
from flask import g

from app.constants.admin_ip import MERCHANT_ADMIN_IP_LIST
from app.extensions import limiter
from app.libs.api_exception import APIException
from app.libs.decorators import check_ip_in_white_list
from app.libs.error_code import AccountNotExistError
from app.logics.token.token_base import MerchantLoginToken
from app.models.merchantoffice.merchant_user import MerchantUser

merchant_auth = HTTPTokenAuth(scheme='Bearer')


@merchant_auth.error_handler
def handle_token_auth_error():
    if isinstance(g.error, APIException):
        return g.error.as_json_response()
    return "Unauthorized Access"


@merchant_auth.verify_token
def verify_credential(token):
    """
    使用basic auth进行JWT token鉴权
    加了装饰器 @auth.login_required 的view都需要先进这个函数进行token鉴权
    :param token:
    :return:
    """

    # 初始化g对象的error属性
    g.error = None

    rst = MerchantLoginToken.verify_token(token)
    if isinstance(rst, (APIException,)):
        # token 验证失败
        g.error = rst
        return False

    # 账户被封处理
    user = MerchantUser.query_user(mid=rst['uid'])
    if not user:
        # 用户不存在
        g.error = AccountNotExistError()
        return False

    g.user = user
    return True


# merchant office 装饰器
merchant_decorators = [check_ip_in_white_list(MERCHANT_ADMIN_IP_LIST), merchant_auth.login_required,
                       limiter.limit("1/second")]
