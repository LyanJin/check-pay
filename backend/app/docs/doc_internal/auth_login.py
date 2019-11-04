from flask_restplus import fields

from app.extensions.ext_api import api_backoffice as api
from app.libs.error_code import ResponseSuccess
from app.constants import auth_code as mobile_constant

##############################################
# API的请求的数据model
##############################################

AdminAccountRegister = api.model('AdminAccountRegister', {
    'account': fields.String(
        required=True,
        description='账号',
        example="kevin",
    ),
    'password': fields.String(
        required=True,
        description='密码,用明文注册',
        example="123456",
    )
})

AdminAccountLogin = api.model('AdminAccountLogin', {
    'account': fields.String(
        required=True,
        description='账号',
        example="kevin",
    ),
    'password': fields.String(
        required=True,
        description='密码',
        example="md5加密后的32为字符串",
    )
})

AdminResetPasswordVerify = api.model('AdminResetPasswordVerify', {
    'ori_password': fields.String(
        required=True,
        description='原密码',
        example="abc123 的md5是：e99a18c428cb38d5f260853678922e03"
    )
})

AdminResetPassword = api.inherit('AdminResetPassword', AdminResetPasswordVerify, {
    'new_password': fields.String(
        required=True,
        description='重置密码',
        example="abc123 的md5是：e99a18c428cb38d5f260853678922e03"
    )
})
##############################################
# API的响应的数据model
##############################################
AdminRegisterResult = api.model('AdminRegisterResult', {
    'md5_password': fields.String(
        required=True,
        description='密码',
        example="md5加密后的32为字符串",
    )
})


class AdminRegisterResponse(ResponseSuccess):
    data_model = AdminRegisterResult


AdminLoginResult = api.model('AdminLoginResult', {
    'token': fields.String(
        required=True,
        description='base64加密后的登录令牌,每个请求传回进行鉴权',
    )
})


class AdminLoginResponse(ResponseSuccess):
    data_model = AdminLoginResult
