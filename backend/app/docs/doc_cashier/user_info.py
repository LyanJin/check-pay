from flask_restplus import fields

from app.extensions.ext_api import api_cashier as api
from app.constants import auth_code as mobile_constant

##############################################
# API的请求的数据model
##############################################
from app.libs.error_code import ResponseSuccess

UserLogin = api.model('UserLogin', {
    'token': fields.String(
        required=True,
        description='用户令牌',
        example="****************************",
        min_length=mobile_constant.TOKEN_MIN_LENGTH,
        max_length=mobile_constant.TOKEN_MAX_LENGTH
    ),
    'test_field': fields.String(
        required=True,
        description='测试字段',
        example='这是测试数据',
        min_length=8,
        max_length=16
    )
})

##############################################
# API的响应的数据model
##############################################

TransferUserQueryResult = api.model('TransferUserQueryResult', {
    'is_auth': fields.Boolean(
        required=True,
        description='是否认证',
        example=True,
    ),
    'transfer_limit': fields.Integer(
        required=True,
        description='转账限额',
        example=4000,
    ),
})


class ResponseTransferUserQueryResult(ResponseSuccess):
    data_model = TransferUserQueryResult

