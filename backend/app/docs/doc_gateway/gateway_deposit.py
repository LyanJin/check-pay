from flask_restplus import fields

from app.enums.trade import PaymentTypeEnum, OrderStateEnum
from app.extensions.ext_api import api_gateway as api
from app.libs.error_code import ResponseSuccess

ResponseSuccess.doc_path = False

###################################################
# API的响应的数据model
##############################################
DocRequestDeposit = api.model('DocRequestDeposit', {
    'sign': fields.String(
        required=True,
        description='(必填,不参与签名)签名',
    ),
    'merchant_id': fields.Integer(
        required=True,
        description='(必填,参与签名)商户ID',
        example=200,
    ),
    'amount': fields.Float(
        required=True,
        description='(必填,参与签名)充值金额，必须是整数或浮点数字符串，最多保留2位小数',
        example="500.34",
    ),
    'mch_tx_id': fields.String(
        required=True,
        description='(必填,参与签名)商户订单号，最大128个字符',
    ),
    'payment_type': fields.String(
        required=True,
        description="(必填,参与签名)" + PaymentTypeEnum.description_name_desc(),
        example=PaymentTypeEnum.ZHIFUBAO.name,
    ),
    'notify_url': fields.String(
        required=True,
        description='(必填,参与签名)回调通知URL',
        example="https://google.com",
    ),
    'user_id': fields.String(
        required=False,
        description='(可选,不参与签名)用户ID',
        example="999",
    ),
    'user_ip': fields.String(
        required=True,
        description='(必填,参与签名)发起请求的用户ip',
        example="192.168.1.1",
    ),
    'result_url': fields.String(
        required=False,
        description='(可选,不参与签名)充值结果展示的重定向URL，不填写则不会跳转',
        example="https://google.com",
    ),
    'extra': fields.String(
        required=False,
        description='(可选,不参与签名)透传数据，在回调通知里面传回',
    ),
})

DocOrderNotify = api.model('DocOrderNotify', {
    'sign': fields.String(
        required=True,
        description='签名',
    ),
    'merchant_id': fields.Integer(
        required=True,
        description='商户ID',
        example=200,
    ),
    'amount': fields.Float(
        required=True,
        description='订单发起金额',
        example="500.34",
    ),
    'tx_amount': fields.Float(
        required=True,
        description='实际交易金额',
        example="500.34",
    ),
    'mch_tx_id': fields.String(
        required=True,
        description='商户订单号，最大128个字符',
    ),
    'sys_tx_id': fields.String(
        required=True,
        description='平台订单号，最大32个字符',
    ),
    'state': fields.String(
        required=True,
        description='订单状态',
        example=OrderStateEnum.description_name_desc(values=[OrderStateEnum.SUCCESS, OrderStateEnum.FAIL]),
    ),
    'extra': fields.String(
        required=False,
        description='(不参与签名)透传数据',
    ),
})

##############################################
# API的响应的数据model
##############################################
DocResponseDeposit = api.model('DocResponseDeposit', {
    'redirect_url': fields.String(
        required=True,
        description='跳转页面URL',
        example="https://google.com",
    ),
    'valid_time': fields.Integer(
        required=True,
        description='订单有效时间，单位秒',
        example=30 * 60,
    ),
    'sys_tx_id': fields.String(
        required=True,
        description='平台订单号,最长32位字符串',
    ),
    'mch_tx_id': fields.String(
        required=True,
        description='商户订单号，最大128个字符',
    ),
})


class GatewayResponseDeposit(ResponseSuccess):
    data_model = DocResponseDeposit
