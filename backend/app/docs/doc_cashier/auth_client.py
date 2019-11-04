from flask_restplus import fields

from app.docs.doc_cashier.auth_code import MobileAuthCode, MobileNumber
from app.enums.account import AccountTypeEnum, AuthTypeEnum, UserPermissionEnum, AccountFlagEnum
from app.extensions.ext_api import api_cashier as api
from app.constants import auth_code as mobile_constant

##############################################
# API的请求的数据model
##############################################
from app.libs.error_code import ResponseSuccess

ClientAuthRegister = api.inherit('ClientAuthRegister', MobileAuthCode, {
    'password': fields.String(
        required=True,
        description='md5之后的密码',
        example="abc123 的md5是：e99a18c428cb38d5f260853678922e03",
        min_length=mobile_constant.PASSWORD_MIN_LENGTH,
        max_length=mobile_constant.PASSWORD_MAX_LENGTH
    ),
    'ac_type': fields.Integer(
        required=True,
        description=AccountTypeEnum.description(),
        example=AccountTypeEnum.MOBILE.value,
    ),
    'auth_type': fields.Integer(
        required=True,
        description=AuthTypeEnum.description(),
        example=AuthTypeEnum.SMS_CODE.value,
    ),
})

ClientAuthLogin = api.inherit('ClientAuthLogin', MobileNumber, {
    'password': fields.String(
        required=True,
        description='md5之后的密码',
        example="abc123 的md5是：e99a18c428cb38d5f260853678922e03",
        min_length=mobile_constant.PASSWORD_MIN_LENGTH,
        max_length=mobile_constant.PASSWORD_MAX_LENGTH
    )
})

##############################################
# API的响应的数据model
##############################################

LoginSuccessResult = api.model('LoginSuccessResult', {
    'token': fields.String(
        required=True,
        description='已经进行base64编码的token, 直接填入http头：Authorization: Bearer {token}'
    ),
    'service_url': fields.String(
        required=True,
        description='客服URL'
    ),
    'permissions': fields.List(
        fields.String,
        required=True,
        description='权限列表，列表为空时没有权限控制，当列表不为空时，只允许列表中设置的权限',
        example=UserPermissionEnum.get_names(),
    ),
    'bind_name': fields.String(
        required=True,
        description='绑定的用户名称'
    ),
    'user_flag': fields.String(
        required=True,
        description='用户标签',
        example=AccountFlagEnum.get_name_list(),
    ),
})


class ResponseSuccessLogin(ResponseSuccess):
    data_model = LoginSuccessResult


##############################################
# API的响应的数据model
##############################################

LoginResult = api.model('LoginResult', {
    'uid': fields.Integer(
        required=True,
        description='用户ID',
        example=10001,
    ),
    'token': fields.String(
        required=True,
        description='token',
    ),
})


class ResponseLogin(ResponseSuccess):
    # 业务数据model
    data_model = LoginResult
