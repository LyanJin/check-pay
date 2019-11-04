from flask_restplus import fields

from app.enums.channel import ChannelConfigEnum
from config import MerchantTypeEnum
from app.enums.balance import ManualAdjustmentType
from app.enums.trade import PaymentFeeTypeEnum, PayMethodEnum, PaymentBankEnum, CostTypeEnum, OrderStateEnum, \
    PayTypeEnum
from app.extensions.ext_api import api_backoffice as api
from app.libs.error_code import ResponseSuccess
from config import MerchantEnum

##############################################
# API的请求的数据model
##############################################


OrderIdCommentDoc = api.model("OrderIdCommentDoc", {
    'order_id': fields.String(
        required=True,
        description='订单ID',
        example="4",
    ),
    'comment': fields.String(
        required=True,
        description='备注信息',
        example="通道没有回调给我啊",
    ),
})



#############################################
# 商户费率查询和商户基本信息
#############################################

DescNamePair = api.model("DescNamePair", {
    "name": fields.String,
    "desc": fields.String
})


NameTypePair = api.model("NameTypePair", {
    "name": fields.String,
    "type": fields.String
})

DescValuePair = api.model("DescValuePair", {
    "desc": fields.String,
    "value": fields.String,
})

MerchantConfig = api.model('MerchantConfig', {
    "merchant_names": fields.List(fields.Nested(NameTypePair), description="可选的商户列表"),
    "payment_methods": fields.List(fields.Nested(DescValuePair), description="支付方式列表"),
    "withdraw_type": fields.List(fields.Nested(DescValuePair), description="出款类型"),
    "channels_withdraw": fields.List(fields.Nested(DescNamePair), description="代付通道列表"),
    "channels_deposit": fields.List(fields.Nested(DescNamePair), description="充值通道列表"),
})


class MerchantConfigResult(ResponseSuccess):
    data_model = MerchantConfig


##############################################
# 商户列表查询和商户详情查询
##############################################

FeeConfig = api.model("FeeConfig", {
    "desc": fields.String,
    "value": fields.String,
    "rate": fields.String
})

ChannelFees = api.model("ChannelFees", {
    "withdraw": fields.String,
    "cost_type": fields.String,
    "deposit": fields.List(fields.Nested(FeeConfig))
})

MerchantItem = api.model('MerchantItem', {
    "id": fields.String,
    "name": fields.String,
    "balance_total": fields.String,
    "balance_available": fields.String,
    "balance_income": fields.String,
    "balance_frozen": fields.String,
    "type": fields.String,
    "domains": fields.String,
    "state": fields.String,
    "channel_fees": fields.Nested(ChannelFees)
})

MerchantList = api.model('MerchantList', {
    'counts': fields.String(
        required=True,
        description='商户总个数',
        example="10"
    ),
    'merchants': fields.List(fields.Nested(MerchantItem)),
})


class MerchantListResult(ResponseSuccess):
    data_model = MerchantList


##############################################
# 新建商户信息
##############################################

DepositTypeList = api.model("Deposit", {
    "name": fields.String(
        required=True,
        description=PayMethodEnum.description_value_desc(),
        example=PayMethodEnum.ZHIFUBAO_H5.value,
    ),
    "value": fields.String(
        required=True,
        description='费率',
        example='3.2'
    ),
    "fee_type": fields.String(
        required=True,
        description=PaymentFeeTypeEnum.description_value_desc(),
        example=PaymentFeeTypeEnum.PERCENT_PER_ORDER.value,
    )
})

WithdrawType = api.model("WithdrawType", {
    "value": fields.String(
        required=True,
        description='提现费率',
        example='2.3'
    ),
    "fee_type": fields.String(
        required=True,
        description=PaymentFeeTypeEnum.description_value_desc(),
        example=PaymentFeeTypeEnum.PERCENT_PER_ORDER.value,
    ),
    "cost_type": fields.String(
        required=True,
        description=CostTypeEnum.description_name_desc(),
        example=CostTypeEnum.MERCHANT.name,
    ),
})

MerchantFeeAdd = api.model('MerchantFeeAdd', {
    'name': fields.String(
        required=True,
        description='商户名称',
        example="test",
    ),
    'type': fields.Integer(
        required=True,
        descriptin=MerchantTypeEnum.description_value_desc(),
        example=MerchantTypeEnum.TEST.value,
    ),
    'deposit_info': fields.List(
        fields.Nested(DepositTypeList)
    ),
    'withdraw_info': fields.Nested(WithdrawType)
})

#####################################################
# 编辑费率
#####################################################

MerchantFeeEdit = api.model('MerchantFeeEdit', {
    'name': fields.String(
        required=True,
        description='商户名称',
        example="test",
    ),
    'deposit_info': fields.List(
        fields.Nested(DepositTypeList)
    ),
    'withdraw_info': fields.Nested(WithdrawType)
})

#####################################################
# 商户余额编辑
#####################################################

MerchantBalanceEdit = api.model('MerchantBalanceEdit', {
    'name': fields.String(
        required=True,
        description='商户名称',
        example=MerchantEnum.description(),
    ),
    'adjustment_type': fields.String(
        required=True,
        description='调整类型',
        example=ManualAdjustmentType.description(),
    ),
    'amount': fields.String(
        required=True,
        description='调整金额（浮点数转为字符串）',
        example="500.34",
    ),
    'reason': fields.String(
        required=True,
        description='原因说明',
        example="原因说明....."
    )
})

#################################################
# 用户提现订单列表
#################################################

QueryWithdrawOrderListDoc = api.model('QueryWithdrawOrderListDoc', {
    'order_id': fields.String(
        required=False,
        description='商户订单号/系统订单号',
        example="TEXT|XXXXX|XXXXXX",
    ),
    'merchant_name': fields.String(
        required=False,
        description='商户名称',
        example=MerchantEnum.description_name_desc() + ", 空字符串则为全部",
    ),
    'channel': fields.String(
        required=False,
        description='通道名称',
        example=ChannelConfigEnum.get_name_list(),
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
    'begin_time': fields.String(
        required=True,
        description='开始时间',
        example="2019-07-01 00:00:00"
    ),
    'end_time': fields.String(
        required=True,
        description='结束时间',
        example="2019-07-25 00:00:00"
    ),
    'state': fields.String(
        required=True,
        description='订单状态',
        example=OrderStateEnum.get_back_desc_list(PayTypeEnum.WITHDRAW) + ", 0为全部",
    ),
    'done_begin_time': fields.String(
        required=False,
        description='开始时间(订单完成时间)',
        example="2019-07-01 00:00:00"
    ),
    'done_end_time': fields.String(
        required=False,
        description='结束时间(订单完成时间)',
        example="2019-07-25 00:00:00"
    ),
})

#################################################
# 用户提现订单详情
#################################################

WithDrawOrderDetailParams = api.model('WithDrawOrderDetailParams', {
    'order_id': fields.String(
        required=True,
        description='订单号',
        example="123",
    )
})

#################################################
# 用户提现订单 用户银行信息获取
#################################################

WithDrawGetBankParams = api.model('WithDrawGetBankParams', {
    'order_id': fields.String(
        required=True,
        description='订单',
        example="123",
    ),
    "merchant": fields.String(
        required=True,
        description='商户名称',
        example="Test",
    )
})

#################################################
# 运营出款操作
#################################################

WithDrawPersonExecuteParams = api.model('WithDrawPersonExecuteParams', {
    'order_id': fields.String(
        required=True,
        description='订单',
        example="123",
    ),
    "merchant": fields.String(
        required=True,
        description='商户名称',
        example="Test",
    )
})

#################################################
# 运营出款操作完成
#################################################

WithDrawPersonExecuteDoneParams = api.model('WithDrawPersonExecuteDoneParams', {
    'order_id': fields.String(
        required=True,
        description='订单',
        example="123",
    ),
    "merchant": fields.String(
        required=True,
        description='商户名称',
        example="Test",
    ),
    "comment": fields.String(
        required=True,
        description='说明',
        example="Test",
    ),
    "fee": fields.String(
        required=True,
        description='手续费',
        example="5",
    )
})

#################################################
# 提现订单 认领
#################################################

AllowedOrder = api.model("AllowedOrder", {
    'order_id': fields.String(
        required=True,
        description='系统订单号',
        example="4",
    ),
    'merchant_name': fields.String(
        required=True,
        description='商户名称',
        example="TEST",
    )

})

#################################################
# 提现订单 代付通道出款
#################################################

WithDrawChannelAllowed = api.model("WithDrawChannelAllowed", {
    'merchant': fields.String(
        required=True,
        description='商户名称',
        example=MerchantEnum.description(),
    ),
    'order_id': fields.String(
        required=True,
        description='订单号',
        example="4",
    ),
    "channel_id": fields.String(
        required=True,
        description='代付渠道',
        example="1",
    )
})

#####################################################
# user bank
#####################################################
UserBankExpect = api.model("UserBankExpect", {
    "bank_type": fields.String(
        required=True,
        description=PaymentBankEnum.description_name_desc(),
        example=PaymentBankEnum.ZHONGGUO.name,
    ),
    'merchant_name': fields.String(
        required=True,
        description='商户名称',
        example="TEST",
    ),
    "amount": fields.String(
        required=True,
        description='提现金额',
        example="5000",
    )
})

######################################################
# 审核参数
######################################################

YearMouthExpect = api.model("YearMouthExpect", {
    "year": fields.String(
        required=True,
        description='年',
        example="2019"),
    'mouth': fields.String(
        required=True,
        description='月',
        example="8",
    )
})

#################################################
# 用户充值订单列表
#################################################

QueryDepositOrderListDoc = api.model('QueryDepositOrderListDoc', {
    'order_id': fields.String(
        required=False,
        description='商户订单号/系统订单号',
        example="TEXT|XXXXX|XXXXXX",
    ),
    'merchant_name': fields.String(
        required=False,
        description='商户名称',
        example=MerchantEnum.description_name_desc() + ", 空字符串则为全部",
    ),
    'channel': fields.String(
        required=False,
        description='通道名称',
        example=ChannelConfigEnum.get_name_list(),
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
    'begin_time': fields.String(
        required=True,
        description='开始时间',
        example="2019-07-01 00:00:00"
    ),
    'end_time': fields.String(
        required=True,
        description='结束时间',
        example="2019-07-25 00:00:00"
    ),
    'state': fields.String(
        required=True,
        description='订单状态',
        example=OrderStateEnum.get_back_desc_list(PayTypeEnum.DEPOSIT) + ", 0为全部",
    ),
    'done_begin_time': fields.String(
        required=False,
        description='开始时间(订单完成时间)',
        example="2019-07-01 00:00:00"
    ),
    'done_end_time': fields.String(
        required=False,
        description='结束时间(订单完成时间)',
        example="2019-07-25 00:00:00"
    ),
})

#################################################
# 手动补单操作
#################################################

CreateDepositOrderParams = api.model('CreateDepositOrderParams', {
    'uid': fields.String(
        required=True,
        description='用户id',
        example="1",
    ),
    "merchant": fields.String(
        required=True,
        description='商户名称',
        example="TEST",
    ),
    "payment_type": fields.String(
        required=True,
        description='支付方式',
        example="10",
    ),
    "channel_id": fields.String(
        required=True,
        description='通道id',
        example="1001",
    ),
    "mch_tx_id": fields.String(
        required=True,
        description='通道订单号',
        example="12xxx3aaaa",
    ),
    "amount": fields.String(
        required=True,
        description='充值金额',
        example="5000",
    ),
    "remark": fields.String(
        required=True,
        description='备注信息',
        example="掉单 手动补单",
    )
})
