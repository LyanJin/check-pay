from flask_restplus import fields

from app.enums.trade import OrderStateEnum, DeliverStateEnum, PayTypeEnum
from app.extensions.ext_api import api_merchantoffice as api
from app.libs.error_code import ResponseSuccess

##############################################
# API的请求的数据model
##############################################

##################
# 商户后台注册
##################
MerchantRegister = api.model('MerchantRegister', {
    'account': fields.String(
        required=True,
        description='账号',
        example="TEST",
    ),
    'password': fields.String(
        required=True,
        description='密码',
        example="md5加密后的32为字符串 e99a18c428cb38d5f260853678922e03  abc123",
    )
})

##################
# 商户后台登陆
##################
AdminMerchantLogin = api.model('AdminMerchantLogin', {
    'account': fields.String(
        required=True,
        description='账号',
        example="TEST",
    ),
    'password': fields.String(
        required=True,
        description='密码',
        example="md5加密后的32为字符串 e99a18c428cb38d5f260853678922e03  abc123",
    )
})
##################
# 商户后台登陆成功 结果返回
##################

MerchantLoginResult = api.model('MerchantLoginResult', {
    'token': fields.String(
        required=True,
        description='base64加密后的登录令牌,每个请求传回进行鉴权',
    )
})


class MerchantLoginResponse(ResponseSuccess):
    data_model = MerchantLoginResult


##########################
# 商户基本信息展示
##########################

MerchantBaseInfoResult = api.model('MerchantBaseInfoResult', {
    'account': fields.String(
        required=True,
        description='当前商户名称',
    ),
    'balance_total': fields.String(
        required=True,
        description='商户总金额',
    ),
    'available_balance': fields.String(
        required=True,
        description='商户可用余额',
    ),
    'incoming_balance': fields.String(
        required=True,
        description='商户在途余额',
    ),
    'frozen_balance': fields.String(
        required=True,
        description='商户冻结余额',
    )
})


class MerchantBaseInfoResponse(ResponseSuccess):
    data_model = MerchantBaseInfoResult


#####################################
# 商户后台 充值订单查询
#####################################

MerchantOrderDeposit = api.model('MerchantOrderDeposit', {
    'order_id': fields.String(
        required=False,
        description='商户订单号/系统订单号',
    ),
    'start_datetime': fields.String(
        required=False,
        description='订单开始时间',
    ),
    'end_datetime': fields.String(
        required=False,
        description='订单结束时间',
    ),
    'page_size': fields.Integer(
        required=True,
        description='单页数据条数',
        example=10,
    ),
    'page_index': fields.Integer(
        required=True,
        description='页码',
        example=1,
    ),
    'state': fields.String(
        required=True,
        description='订单状态',
        example="0：全部，10: 未支付， 30: 支付成功， 40： 支付失败"
    )
})

#################################
# 商户后台 充值订单查询
#################################

DepositOrderItem = api.model("DepositOrderItem", {
    "sys_tx_id": fields.String(required=True, description="系统订单号", example="00001"),
    "mch_tx_id": fields.String(required=True, description="商户订单号", example="0001"),
    "payment_type": fields.String(required=True, description="支付方式", example="支付宝"),
    "amount": fields.String(required=True, description="发起金额", example="500"),
    "tx_amount": fields.String(required=True, description="实际支付金额", example="500"),
    "fee": fields.String(required=True, description="手续费", example="2"),
    "create_time": fields.String(required=True, description="创建时间", example="2019-09-23 09:21:34"),
    "done_time": fields.String(required=True, description="完成时间", example="2019-09-23  09:22:08"),
    "state": fields.String(required=True, description="订单状态", example=OrderStateEnum.get_desc_value_pairs()),
    "deliver": fields.String(required=True, description="订单状态", example=DeliverStateEnum.get_desc_value_pairs()),
})

MerchantDepositOrderList = api.model('MerchantDepositOrderList', {
    'entries': fields.List(fields.Nested(DepositOrderItem)),
    'total': fields.String(
        required=True, description="总条数", example="518"
    )
})


class MerchantDepositOrderResult(ResponseSuccess):
    data_model = MerchantDepositOrderList


#####################################
# 商户后台 提现订单查询
#####################################

MerchantOrderWithDraw = api.model('MerchantOrderWithDraw', {
    'order_id': fields.String(
        required=False,
        description='商户订单号/系统订单号',
    ),
    'start_datetime': fields.String(
        required=False,
        description='订单开始时间',
    ),
    'end_datetime': fields.String(
        required=False,
        description='订单结束时间',
    ),
    'page_size': fields.Integer(
        required=True,
        description='单页数据条数',
        example=10,
    ),
    'page_index': fields.Integer(
        required=True,
        description='页码',
        example=1,
    ),
    'state': fields.String(
        required=True,
        description='订单状态',
        example="0：全部，10: 未支付， 30: 支付成功， 40： 支付失败"
    )
})

#################################
# 商户后台 提现订单查询
#################################

WithdrawOrderItem = api.model("WithdrawOrderItem", {
    "sys_tx_id": fields.String(required=True, description="系统订单号", example="00001"),
    "mch_tx_id": fields.String(required=True, description="商户订单号", example="0001"),
    "amount": fields.String(required=True, description="提现金额", example="500"),
    "fee": fields.String(required=True, description="手续费", example="2"),
    "account_name": fields.String(required=True, description="开户名", example="郭爱珍"),
    "bank_name": fields.String(required=True, description="开户银行", example="中国工商银行"),
    "branch": fields.String(required=True, description="开户地址", example="X省X市XXXX"),
    "card_no": fields.String(required=True, description="银行卡号", example="6228 4818 3904 0687 576"),
    "create_time": fields.String(required=True, description="创建时间", example="2019-09-23 09:21:34"),
    "done_time": fields.String(required=True, description="完成时间", example="2019-09-23  09:22:08"),
    "state": fields.String(required=True, description="订单状态", example=OrderStateEnum.get_desc_value_pairs()),
    "deliver": fields.String(required=True, description="订单状态", example=DeliverStateEnum.get_desc_value_pairs()),
})

MerchantWithdrawOrderList = api.model('MerchantWithdrawOrderList', {
    'entries': fields.List(fields.Nested(WithdrawOrderItem)),
    'total': fields.String(
        required=True, description="总条数", example="518"
    )
})


class MerchantWithdrawOrderResult(ResponseSuccess):
    data_model = MerchantWithdrawOrderList


######################################################
# 订单通知
######################################################
OrderStateNotifyDoc = api.model("OrderStateNotifyDoc", {
    "order_id": fields.Integer(
        required=True,
        description='订单号',
        example=11111,
    ),
    "type": fields.String(
        required=True,
        description='订单类型',
        example=PayTypeEnum.description(),
    )
})
