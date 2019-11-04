"""
用户充值提现模块相关的API接口文档描述
"""
from flask_restplus import fields

from app.enums.channel import ChannelConfigEnum
from app.enums.third_enum import SdkRenderType
from app.enums.trade import PaymentTypeEnum, BalanceTypeEnum, PayTypeEnum, OrderStateEnum, PayMethodEnum
from app.libs.error_code import ResponseSuccess
from app.extensions.ext_api import api_cashier as api

##############################################
# 获取用户充值限额
##############################################
DepositLimitConfigResult = api.model('DepositLimitResult', {
    'limit_min': fields.String(
        required=True,
        description='用户充值限额下限',
        example="500",
    ),
    'limit_max': fields.String(
        required=True,
        description='用户充值限额上限',
        example="50000",
    )
})


class ResponseDepositLimitConfig(ResponseSuccess):
    # 业务数据model
    data_model = DepositLimitConfigResult


##############################################
# 获取用户余额
##############################################
UserBalanceResult = api.model('UserBalanceResult', {
    'balance': fields.String(
        required=True,
        description='用户余额',
        example="500",
    ),
    'has_trade_pwd': fields.Boolean(
        required=True,
        description='是否设置交易密码',
        example="true or false",
    ),
})


class ResponseUserBalance(ResponseSuccess):
    # 业务数据model
    data_model = UserBalanceResult


########################################################
# 获取支付方式
########################################################

DescValuePair = api.model("DescValuePair", {
    "desc": fields.String(
        description="支付方式描述",
        example=PaymentTypeEnum.ZHIFUBAO.desc,
    ),
    "value": fields.String(
        description='支付方式数值',
        example=PaymentTypeEnum.ZHIFUBAO.value,
    ),
})

DescValueChannelPair = api.model("DescValueChannelPair", {
    "desc": fields.String(
        description="支付方式描述",
        example=PaymentTypeEnum.get_desc_list(),
    ),
    "value": fields.String(
        description='支付方式数值',
        example=PaymentTypeEnum.description_value_desc(),
    ),
    "channel_id": fields.String(
        description='通道ID',
        example="通道ID，发起充值时原样传回",
    ),
    "channel_prompt": fields.String(
        description='通道备注信息',
        example="农行卡不能使用",
    ),
    "limit_min": fields.Float(
        description='最小限额',
        example=100.19,
    ),
    "limit_max": fields.Float(
        description='最大限额',
        example=5000.19,
    ),
})

PaymentTypeResult = api.model('PaymentTypeResult', {
    'payment_type_list': fields.List(fields.Nested(DescValueChannelPair))
})


class ResponsePaymentType(ResponseSuccess):
    # 业务数据model
    data_model = PaymentTypeResult


#########################################################
# 用户提现
#########################################################

WithDrawLimitConfigResult = api.model('DepositLimitResult', {
    'balance': fields.String(
        required=True,
        description='用户余额',
        example="500"
    ),
    'limit_min': fields.String(
        required=True,
        description='用户充值限额下限',
        example="500"
    ),
    'limit_max': fields.String(
        required=True,
        description='用户充值限额上限',
        example="50000",
    )
})


class ResponseWithdrawLimitConfig(ResponseSuccess):
    # 业务数据model
    data_model = WithDrawLimitConfigResult


#########################################################
# 提现支持的银行
#########################################################


DescValuePair = api.model("DescValuePair", {
    "desc": fields.String(
        description="支付方式描述",
        example=PaymentTypeEnum.ZHIFUBAO.desc,
    ),
    "value": fields.String(
        description='支付方式数值',
        example=PaymentTypeEnum.ZHIFUBAO.value,
    ),
})

WithdrawBankResult = api.model('WithdrawBankResult', {
    'banks': fields.List(fields.Nested(DescValuePair))
})


class ResponseBankWithdraw(ResponseSuccess):
    # 业务数据model
    data_model = WithdrawBankResult


####################################################################
# payment/type/list request form
####################################################################

PaymentTypeListRequestDoc = api.model("PaymentTypeListRequestDoc", {
    'amount': fields.String(
        required=True,
        description='充值金额',
        example="400.03"
    ),
})

####################################################################
# deposit request form
####################################################################

DepositRequest = api.model("DepositRequest", {
    'payment_type': fields.String(
        required=True,
        description='充值方式',
        example=PaymentTypeEnum.description()
    ),
    'amount': fields.String(
        required=True,
        description='订单金额',
        example="400.03"
    ),
    'channel_id': fields.String(
        required=True,
        description='通道Id',
        example="101"
    )
})

#########################################################
# 订单支付url
#########################################################

RedirectUrlResult = api.model('RedirectUrlResult', {
    'redirect_url': fields.String(
        required=True,
        description='用户支付url',
        example="https://..."
    ),
    'pay_type': fields.String(
        required=True,
        description='第三方支付方式',
        example=SdkRenderType.description()
    )
})


class ResponseRedirectUrl(ResponseSuccess):
    # 业务数据model
    data_model = RedirectUrlResult


##################################################
# 获取用户订单信息
##################################################

OrderEntry = api.model("OrderEntry", {
    "tx_id": fields.String(
        description="交易流水号",
        example="",
    ),
    "amount": fields.String(
        description='订单金额',
        example="560.03",
    ),
    "create_time": fields.String(
        description='订单发起时间',
        example="2019-07-29"
    ),
    "status": fields.String(
        description='订单状态',
        example=OrderStateEnum.get_desc_list()
    ),
    "order_type": fields.String(
        description='订单类型',
        example=PayTypeEnum.get_desc_list()
    ),
    "pay_method": fields.String(
        description='支付方式',
        example=PayMethodEnum.get_desc_list()
    ),

    # 转账字段
    "out_account": fields.String(
        description='出款手机手号码',
        example="",
    ),
    "in_account": fields.String(
        description='收款手机号码',
        example="",
    ),
    "comment": fields.String(
        description='备注信息',
        example="",
    ),

    # 提现特有字段
    "bank_info": fields.String(
        description='提现银行',
        example="建设银行(1234)李小白",
    ),
    "fee": fields.String(
        description='用户提现手续费',
        example="1.22",
    ),
})

UserOrderListResult = api.model('UserOrderListResult', {
    "order_entry_list": fields.List(fields.Nested(OrderEntry)),
    "order_entry_total": fields.String(
        description='总条数',
        example="218"
    )
})


class ResponseOrderEntryList(ResponseSuccess):
    # 业务数据model
    data_model = UserOrderListResult


##########################################################
# 用户提现： 请求创建
##########################################################
WithdrawRequestDoc = api.model("WithdrawRequest", {
    'amount': fields.String(
        required=True,
        description='提现金额',
        example="300.4"
    ),
    'user_bank': fields.String(
        required=True,
        description='用户银行卡编号',
        example="2"
    ),
    'trade_password': fields.String(
        required=True,
        description='支付密码',
        example="1234566"
    )
})

##########################################################
# 钱包用户订单查询
##########################################################

UserOrderSelect = api.model("UserOrderSelect", {
    'year': fields.String(
        required=True,
        description='年',
        example="2019"
    ),
    'mouth': fields.String(
        required=True,
        description='月',
        example="7"
    ),
    'page_size': fields.Integer(
        required=True,
        description='单页数据条数',
        example=10
    ),
    'page_index': fields.Integer(
        required=True,
        description='页码',
        example=0
    ),
    "payment_type": fields.String(
        # required=True,
        description='充值/提现',
        example=PayTypeEnum.description(),
    )
})

##########################################################
# BestPay 充值通知
##########################################################

OrderTransfer = api.model("OrderTransfer", {
    "tx_id": fields.String(
        description="交易流水号",
        required=True,
        example="",
    ),
    "amount": fields.String(
        description='存款金额',
        required=True,
        example="560.03",
    ),
    "card_number": fields.String(
        description='存款卡号',
        required=True,
        example="6224 **** ***** **** 537"
    ),
    "bank_name": fields.String(
        description='存款银行',
        required=True,
        example="中国银行"
    ),
    "user_name": fields.String(
        description='用户名称',
        required=True,
        example="张三"
    ),
    "payment_method": fields.String(
        description='转账方式',
        required=True,
        example="银行卡转银行卡",
    ),
    "client_bank": fields.String(
        description='发起转账银行',
        required=True,
        example="",
    ),
    "channel_id": fields.String(
        description='通道id',
        required=True,
        example="",
    ),
    "fee": fields.String(
        description='手续费',
        example=""
    ),
    "remark": fields.String(
        description="备注",
        example="2344"
    )
})
