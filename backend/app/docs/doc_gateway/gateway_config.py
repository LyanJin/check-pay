from flask_restplus import fields

from app.enums.trade import PaymentTypeEnum, PaymentBankEnum
from app.extensions.ext_api import api_gateway as api
from app.libs.error_code import ResponseSuccess

ResponseSuccess.doc_path = False

###################################################
# API的响应的数据model
##############################################
DocRequestConfig = api.model('DocRequestConfig', {
    'sign': fields.String(
        required=True,
        description='(必填,不参与签名)签名',
        example="",
    ),
    'merchant_id': fields.Integer(
        required=True,
        description='(必填,参与签名)商户ID',
        example="200",
    ),
    'user_id': fields.String(
        required=False,
        description='(可选,不参与签名)用户ID',
        example="999",
    ),
    'user_ip': fields.String(
        required=True,
        description='(可选,不参与签名)用户ID',
        example="999",
    ),
})


##############################################
# API的响应的数据model
##############################################
PaymentConfig = api.model('PaymentConfig', {
    "name": fields.String(
        description=PaymentTypeEnum.description_name_desc(),
        example=PaymentTypeEnum.ZHIFUBAO.name,
    ),
    "limit_min": fields.Float(
        description='最小限额',
        example="100.19",
    ),
    "limit_max": fields.Float(
        description='最大限额',
        example="5000.19",
    ),
    "fixed_amounts": fields.List(
        fields.Float(
            example="50.19",
        ),
        description='限额列表',
    ),
})

WithdrawConfig = api.model('WithdrawConfig', {
    "limit_min": fields.Float(
        description='最小限额',
        example="100.19",
    ),
    "limit_max": fields.Float(
        description='最大限额',
        example="5000.19",
    ),
})


DocResponseConfig = api.model('DocResponseConfig', {
    'payment_types': fields.List(
        fields.Nested(PaymentConfig),
        description='支付类型及其限额列表',
    ),
    'withdraw_config': fields.Nested(WithdrawConfig),
})


class GatewayResponseConfig(ResponseSuccess):
    data_model = DocResponseConfig
