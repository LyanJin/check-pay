from flask_restplus import fields

from app.enums.trade import PaymentBankEnum
from app.extensions.ext_api import api_gateway as api
from app.libs.error_code import ResponseSuccess

ResponseSuccess.doc_path = False

###################################################
# API的响应的数据model
##############################################
DocRequestWithdraw = api.model('DocRequestWithdraw', {
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

    'bank_type': fields.Integer(
        required=True,
        description='(必填,参与签名)' + PaymentBankEnum.description_name_desc(),
        example=PaymentBankEnum.ZHONGGUO.name,
    ),
    'card_no': fields.String(
        required=True,
        description='(必填,参与签名)收款卡号',
        example="93838294912",
    ),
    'account_name': fields.String(
        required=True,
        description='(必填,参与签名)收款人姓名',
        example="张三",
    ),
    'branch': fields.String(
        required=False,
        description='(可选,不参与签名)支行名称',
        example="中国银行深圳支行",
    ),
    'province': fields.String(
        required=True,
        description='(必填,参与签名)省份名称',
        example="广东",
    ),
    'city': fields.String(
        required=True,
        description='(必填,参与签名)城市名称',
        example="深圳",
    ),
    'extra': fields.String(
        required=False,
        description='(可选,不参与签名)透传数据，在回调通知里面传回',
    ),
})


##############################################
# API的响应的数据model
##############################################
DocResponseWithdraw = api.model('DocResponseWithdraw', {
    'sys_tx_id': fields.String(
        required=True,
        description='平台订单号,最长32位字符串',
    ),
    'mch_tx_id': fields.String(
        required=True,
        description='商户订单号，最大128个字符',
    ),
})


class GatewayResponseWithdraw(ResponseSuccess):
    data_model = DocResponseWithdraw
