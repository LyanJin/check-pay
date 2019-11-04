"""
短信模块相关的API接口文档描述
"""
from flask_restplus import fields

from app.enums.trade import PaymentBankEnum
from app.libs.error_code import ResponseSuccess, PaymentPasswordError
from app.extensions.ext_api import api_cashier as api
from app.constants import auth_code as mobile_constant

##############################################
# API的请求的数据model
##############################################
MobileNumber = api.model('MobileNumber', {
    'number': fields.String(
        required=True,
        description='手机区号+号码',
        example="+8618912341234",
        min_length=mobile_constant.NUMBER_MIN_LENGTH,
        max_length=mobile_constant.NUMBER_MAX_LENGTH,
    ),
})

ResetPasswordVerify = api.model('ResetPasswordVerify', {
    'ori_password': fields.String(
        required=True,
        description='原始密码',
        example="abc123 的md5是：e99a18c428cb38d5f260853678922e03",
        min_length=mobile_constant.PASSWORD_MIN_LENGTH,
        max_length=mobile_constant.PASSWORD_MAX_LENGTH
    )
})

ResetPassword = api.inherit('ResetPassword', ResetPasswordVerify, {
    'new_password': fields.String(
        required=True,
        description='重置密码',
        example="abc123 的md5是：e99a18c428cb38d5f260853678922e03",
        min_length=mobile_constant.PASSWORD_MIN_LENGTH,
        max_length=mobile_constant.PASSWORD_MAX_LENGTH
    )
})

MobileAuthCode = api.inherit('MobileAuthCode', MobileNumber, {
    'auth_code': fields.String(
        required=True,
        description='短信动态验证码',
        example="1234",
        min_length=mobile_constant.AUTH_CODE_LENGTH,
        max_length=mobile_constant.AUTH_CODE_LENGTH,
    ),
})

PassWordAuthCode = api.inherit('PassWordAuthCode', MobileAuthCode, {
    'password': fields.String(
        required=True,
        description='设置密码',
        example="abc123 的md5是：e99a18c428cb38d5f260853678922e03",
        min_length=mobile_constant.PASSWORD_MIN_LENGTH,
        max_length=mobile_constant.PASSWORD_MAX_LENGTH
    )
})


PaymentPassword = api.model('PaymentPassword', {
    'payment_password': fields.String(
        required=True,
        description='支付密码6位数字',
        example="156753 的md5是：b943a52cc24dcdd12bf2ba3afda92351",
        min_length=mobile_constant.PAYMENT_PASSWORD_LENGTH,
        max_length=mobile_constant.PAYMENT_PASSWORD_LENGTH,
    ),
})

ResetPaymentPasswordVerify = api.model('ResetPaymentPasswordVerify', {
    'ori_payment_password': fields.String(
        required=True,
        description='原始支付密码',
        example="156753 的md5是：b943a52cc24dcdd12bf2ba3afda92351",
        min_length=mobile_constant.PAYMENT_PASSWORD_LENGTH,
        max_length=mobile_constant.PAYMENT_PASSWORD_LENGTH
    )
})

ResetPaymentPassword = api.inherit('ResetPaymentPassword', ResetPaymentPasswordVerify, {
    'new_payment_password': fields.String(
        required=True,
        description='修改支付密码',
        example="156753 的md5是：b943a52cc24dcdd12bf2ba3afda92351",
        min_length=mobile_constant.PAYMENT_PASSWORD_LENGTH,
        max_length=mobile_constant.PAYMENT_PASSWORD_LENGTH
    )
})


SetForgetPaymentPassword = api.inherit('SetForgetPaymentPassword', MobileAuthCode, {
    'new_payment_password': fields.String(
        required=True,
        description='重置支付密码',
        example="156753 的md5是：b943a52cc24dcdd12bf2ba3afda92351",
        min_length=mobile_constant.PAYMENT_PASSWORD_LENGTH,
        max_length=mobile_constant.PAYMENT_PASSWORD_LENGTH
    )
})


BankCardId = api.model('BankCardId', {
    'card_id': fields.String(
        required=True,
        description='银行卡卡号',
        example="6212260405014627955"
    ),
})

BankCardParams = api.inherit('BankCard',PaymentPassword, {
    'bank_name': fields.String(
        required=True,
        description='银行名称',
        example="中国工商银行",
    ),
    'bank_code': fields.String(
        required=True,
        description='银行编码',
        example="ICBC",
    ),
    'card_no': fields.String(
        required=True,
        description='银行卡卡号',
        example="6212260405014627955",
        min_length=12,
        max_length=19,
    ),
    'account_name': fields.String(
        required=True,
        description='开户人姓名',
        example="张三",
        min_length=2,
        max_length=20,
    ),
    'branch': fields.String(
        required=True,
        description='支行',
        example="广东东莞东莞市长安镇支行",
    ),
    'province': fields.String(
        required=True,
        description='省份',
        example="广东省",
    ),
    'city': fields.String(
        required=True,
        description='市',
        example="东莞市",
    ),
})


BankCardDeleteParams = api.inherit('BankCardDeleteParams',PaymentPassword, {
    'bank_card_id': fields.String(
        required=True,
        description='银行卡id',
        example="123",
    ),   
})

TransferParam = api.inherit('TransferParam',PaymentPassword, {
    'amount': fields.String(
        required=True,
        description='转账金额最小0.01 最大45000',
        example="450",
    ),
    'zone': fields.String(
        required=True,
        description='手机区号',
        example="+86",
    ),
    'number': fields.String(
        required=True,
        description='手机号码，不带区号',
        example="18912341234",
    ),
    'comment': fields.String(
        required=False,
        description='转账说明最多10个字符，非必填',
        example="转账说明",
    ), 
})


TransferAccountQueryDoc = api.model('TransferAccountQueryDoc', {
    'zone': fields.String(
        required=False,
        description='区号',
        example="+86",
    ),
    'account': fields.String(
        required=True,
        description='手机区号或昵称',
        example='18992929292',
    ),
})


##############################################
# API的响应的数据model
##############################################
BooleanResult = api.model('BooleanResult', {
    'result': fields.Boolean(
        required=True,
        description='布尔结果',
        example=True,
    ),
})


class ResponseCodeAuth(ResponseSuccess):
    # 业务数据model
    data_model = BooleanResult


PaymentPasswordRemaintimesResult = api.model('PaymentPasswordRemaintimesResult', {
    'times': fields.String(
        required=True,
        description='支付密码剩余可以输入的次数',
        example="1",
    ),
})


class ResponsePaymentPasswordRemaintimes(PaymentPasswordError):
    # 业务数据model
    data_model = PaymentPasswordRemaintimesResult


BankItemPair = api.model("BankItemPair", {
    "bank_name": fields.String(
        description="银行名称",
        example="中国工商银行",
    ),
    "bank_code": fields.String(
        description='支付方式数值',
        example="ICBC",
    ),
})

BankResult = api.model('BankResult', {
    'banks': fields.List(fields.Nested(BankItemPair))
})


class ResponseBanks(ResponseSuccess):
    # 业务数据model
    data_model = BankResult


BankLocationResult = api.model('BankLocationResult', {
    'province': fields.String(
        required=True,
        description='银行卡省份',
        example="河北省",
    ),
    'city': fields.String(
        required=True,
        description='银行卡城市',
        example="邯郸",
    ),
    'bank_code': fields.String(
        required=True,
        description='银行编码',
        example="ICBC",
    ),
    'bank_name': fields.String(
        required=True,
        description='银行名称',
        example="中国工商银行",
    ),
})


class ResponseBankLocation(ResponseSuccess):
    # 业务数据model
    data_model = BankLocationResult


BankCardItemPair = api.model("BankCardItemPair", {
    "id": fields.String(
        description="银行卡id",
        example="123",
    ),
    "bank_name": fields.String(
        description="银行名称",
        example="中国工商银行",
    ),
    "bank_code": fields.String(
        description='支付方式数值',
        example="ICBC",
    ),
    "account_name": fields.String(
        description='开户姓名',
        example="张三",
    ),
    "bank_idx": fields.String(
        description='银行卡index',
        example=PaymentBankEnum.description(),
    ),
    "card_no": fields.String(
        description='银行卡卡号只显示最后几位',
        example="************3214",
    ),
})

BankCardResult = api.model('BankCardResult', {
    'bankcards': fields.List(fields.Nested(BankCardItemPair))
})


class ResponseBankCards(ResponseSuccess):
    # 业务数据model
    data_model = BankCardResult
