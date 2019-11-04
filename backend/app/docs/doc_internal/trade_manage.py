from flask_restplus import fields

from app.enums.account import AccountFlagEnum
from config import MerchantTypeEnum
from app.enums.balance import ManualAdjustmentType
from app.enums.trade import PaymentFeeTypeEnum, PayMethodEnum, OrderSourceEnum, OrderStateEnum, DeliverTypeEnum, \
    DeliverStateEnum, PaymentBankEnum, PayTypeEnum
from app.extensions.ext_api import api_backoffice as api
from app.libs.error_code import ResponseSuccess
from config import MerchantEnum

###################################################
# withdraw list
###################################################

NameTypePair = api.model("NameTypePair", {
    "name": fields.String(
        description=MerchantEnum.description(),
        example=MerchantEnum.QF2.name,
    ),
    "type": fields.String(
        description=MerchantTypeEnum.description(),
        example=MerchantTypeEnum.NORMAL.value,
    )
})

DescValuePair = api.model("DescValuePair", {
    "desc": fields.String(
        description="支付方式描述",
        example=PayMethodEnum.WEIXIN_H5.desc,
    ),
    "value": fields.String(
        description='支付方式数值',
        example=PayMethodEnum.WEIXIN_H5.value,
    ),
})

WithdrawItem = api.model("WithdrawItem", {
    "uid": fields.String(required=True, description="用户id", example="0001"),
    "order_id": fields.String(required=True, description="order_id", example="4"),
    "sys_tx_id": fields.String(required=True, description="系统订单号", example="00001"),
    "mch_tx_id": fields.String(required=True, description="商户订单号", example="0001"),
    "merchant": fields.String(required=True, description="商户名称", example="TEST"),
    "source": fields.String(required=True, description="订单来源", example="测试用户"),
    "amount": fields.String(required=True, description="提现金额", example="5000"),
    "create_time": fields.String(required=True, description="创建时间", example="2019-01-23 09:21:34"),
    "state": fields.String(required=True, description="订单状态", example=OrderStateEnum.get_value_list()),
    "operator": fields.String(required=True, description="操作员", example="kv"),
    "deliver": fields.String(required=True, description="通知状态", example=DeliverStateEnum.get_value_list()),
    "user_flag": fields.String(required=True, description="用户标签", example=AccountFlagEnum.get_name_list()),
})

AllWithdrawList = api.model('AllWithdrawList', {
    'entries': fields.List(fields.Nested(WithdrawItem)),
    'total': fields.String(
        required=True, description="总条数", example="518"
    )
})


class AllWithdrawResult(ResponseSuccess):
    data_model = AllWithdrawList


WithdrawReviewItem = api.model("WithdrawReviewItem", {
    "uid": fields.String(required=True, description="用户id", example="0001"),
    "order_id": fields.String(required=True, description="order_id", example="4"),
    "sys_tx_id": fields.String(required=True, description="系统订单号", example="00001"),
    "source": fields.String(required=True, description="订单来源", example="测试用户"),
    "state": fields.String(required=True, description="订单状态", example=OrderStateEnum.get_value_list()),
    "merchant": fields.String(required=True, description="商户", example="TEST"),
    "amount": fields.String(required=True, description="提现金额", example="5000"),
    "create_time": fields.String(required=True, description="创建时间", example="2019-01-23 09:21:34"),
    "done_time": fields.String(required=True, description="完成时间", example="2019-03-28  08:50:08"),
    "bank_name": fields.String(required=True, description="开户行", example="中国银行"),
    "bank_type": fields.String(
        required=True,
        description=PaymentBankEnum.description_name_desc(),
        example=PaymentBankEnum.ZHONGGUO.name,
    ),
    "user_flag": fields.String(required=True, description="用户标签", example=AccountFlagEnum.get_name_list()),
})

ReviewWithdrawList = api.model('ReviewWithdrawList', {
    'entries': fields.List(fields.Nested(WithdrawReviewItem)),
    'total': fields.String(
        required=True, description="总条数", example="518"
    ),
    "operator": fields.String(required=True, description="总条数", example="操作员")
})


class ReviewWithdrawResult(ResponseSuccess):
    data_model = ReviewWithdrawList


######################################################################
# 运营选择 代付通道 返回当前可用的代付通道
######################################################################

WithdrawChannelItem = api.model("WithdrawReviewItem", {
    "key": fields.String(required=True, description="可选渠道", example="立马付996633"),
    "value": fields.String(required=True, description="渠道id", example="4")})

WithdrawChannelList = api.model('WithdrawChannelList', {
    'entries': fields.List(fields.Nested(WithdrawChannelItem))
})


class WithdrawChannelResult(ResponseSuccess):
    data_model = WithdrawChannelList


#######################################################
# 提现订单详情
#######################################################

WithdrawOrderItemHead = api.model("WithdrawOrderItemHead", {
    "source": fields.String(required=True, description="订单来源", example="测试用户"),
    "op_account": fields.String(required=True, description="操作员", example="MK"),
    "deliver_type": fields.String(required=True, description="出款类型", example="代付"),
    "create_time": fields.String(required=True, description="创建时间", example="2019-03-28  08:50:08"),
    "alloc_time": fields.String(required=True, description="认领时间", example="2019-03-28  08:50:08"),
    "deal_time": fields.String(required=True, description="处理时间", example="2019-03-28  08:50:08"),
    "done_time": fields.String(required=True, description="完成时间", example="2019-03-28  08:50:08"),
    "mch_tx_id": fields.String(required=True, description="商户订单号", example="5000"),
    "sys_tx_id": fields.String(required=True, description="系统订单号", example="2019-01-23 09:21:34"),
    "state": fields.String(required=True, description="状态", example="提现成功"),
    "settle": fields.String(required=True, description="结算状态", example="未结算"),
    "deliver": fields.String(required=True, description="通知状态", example=DeliverStateEnum.get_value_list()),
    "amount": fields.String(required=True, description="提现金额", example="5000.00")
})

order_merchant_info = api.model("order_merchant_info", {
    "merchant_name": fields.String(required=True, description="商户名称", example="QF2"),
    "fee": fields.String(required=True, description="手续费", example="3.44"),
    "cost": fields.String(required=True, description="成本金额", example="2.00"),
    "profit": fields.String(required=True, description="收入金额", example="1.44"),
    "withdraw_type": fields.String(required=True, description="类型", example="用户提现")
})

deliver_info = api.model("deliver_info", {
    "channel_name": fields.String(required=True, description="通道", example="立马付"),
    "mch_id": fields.String(required=True, description="通道商户号", example="61135"),
    "channel_tx_id": fields.String(required=True, description="通道订单号", example="453432345")
})

user_info = api.model("user_info", {
    "user_id": fields.String(required=True, description="用户Id", example="123"),
    "ip": fields.String(required=True, description="ip", example="61135"),
    "location": fields.String(required=True, description="地区", example="中国"),
    "device": fields.String(required=True, description="设备", example="453432345")
})

event_log_list = api.model("event_log_list", {
    "operate_type": fields.String(required=True, description="操作类型", example="认领订单"),
    "operator": fields.String(required=True, description="操作员", example="Kevin"),
    "result": fields.String(required=True, description="执行结果", example="成功"),
    "operate_time": fields.String(required=True, description="操作时间", example="2019-01-23 09:21:34"),
    "comment": fields.String(required=True, description="备注信息", example="补单啦"),
})

WithdrawOrderDetail = api.model('WithdrawOrderDetail', {
    'detail_head': fields.Nested(WithdrawOrderItemHead),
    'order_merchant_info': fields.Nested(order_merchant_info),
    'deliver_info': fields.Nested(deliver_info),
    'user_info': fields.Nested(user_info),
    'event_log_list': fields.List(fields.Nested(event_log_list))
})


class WithdrawOrderDetailResult(ResponseSuccess):
    data_model = WithdrawOrderDetail


######################################################################
# 运营选择 代付通道 返回当前可用的代付通道
######################################################################

WithdrawBankInfo = api.model("WithdrawBankInfo", {
    "amount": fields.String(required=True, description="提现金额", example="5000"),
    "account_name": fields.String(required=True, description="开户名", example="张三"),
    "card_no": fields.String(required=True, description="银行卡号", example="6221 1234 5678 1234"),
    "bank_name": fields.String(required=True, description="开户银行", example="招商银行"),
    "province": fields.String(required=True, description="省份", example="广东省"),
    "city": fields.String(required=True, description="城市", example="深圳市"),
    "branch": fields.String(required=True, description="支行", example="卧龙分行")
})

WithdrawBankEntry = api.model('WithdrawBankEntry', {
    'bank_entry': fields.Nested(WithdrawBankInfo)
})


class WithdrawBankEntryResult(ResponseSuccess):
    data_model = WithdrawBankEntry


DepositOrderItem = api.model("DepositOrderItem", {
    "uid": fields.String(required=True, description="用户id", example="0001"),
    "order_id": fields.String(required=True, description="order_id", example="4"),
    "sys_tx_id": fields.String(required=True, description="系统订单号", example="00001"),
    "mch_tx_id": fields.String(required=True, description="商户订单号", example="0001"),
    "merchant": fields.String(required=True, description="商户名称", example="TEST"),
    "channel": fields.String(required=True, description="通道名称", example="yz支付宝"),
    "mch_id": fields.String(required=True, description="通道商户号", example="1001"),
    "source": fields.String(required=True, description="订单来源", example="测试用户"),
    "amount": fields.String(required=True, description="订单发起金额", example="5000"),
    "tx_amount": fields.String(required=True, description="实际支付金额", example="5000"),
    "create_time": fields.String(required=True, description="创建时间", example="2019-01-23 09:21:34"),
    "done_time": fields.String(required=True, description="完成时间", example="2019-03-28  08:50:08"),
    "state": fields.String(required=True, description="订单状态", example=OrderStateEnum.get_value_list()),
    "deliver": fields.String(required=True, description="通知状态", example=DeliverStateEnum.get_value_list()),
    "user_flag": fields.String(required=True, description="用户标签", example=AccountFlagEnum.get_name_list()),
})

DepositOrderList = api.model('DepositOrderList', {
    'entries': fields.List(fields.Nested(DepositOrderItem)),
    'total': fields.String(
        required=True, description="总条数", example="518"
    )
})


class DepositOrderResult(ResponseSuccess):
    data_model = DepositOrderList


#######################################################
# 充值订单详情
#######################################################

DepositOrderItemHead = api.model("DepositOrderItemHead", {
    "source": fields.String(required=True, description="充值类型", example="线上支付"),
    "create_time": fields.String(required=True, description="创建时间", example="2019-03-28  08:50:08"),
    "done_time": fields.String(required=True, description="完成时间", example="2019-03-28  08:50:08"),
    "mch_tx_id": fields.String(required=True, description="商户订单号", example="5000"),
    "sys_tx_id": fields.String(required=True, description="系统订单号", example="2019-01-23 09:21:34"),
    "state": fields.String(required=True, description="状态", example="提现成功"),
    "settle": fields.String(required=True, description="结算状态", example="未结算"),
    "deliver": fields.String(required=True, description="通知状态", example=DeliverStateEnum.get_value_list()),
    "amount": fields.String(required=True, description="发起金额", example="5000.00"),
})

order_merchant_info_deposit = api.model("order_merchant_info_deposit", {
    "merchant_name": fields.String(required=True, description="商户名称", example="QF2"),
    "offer": fields.String(required=True, description="优惠金额", example="0"),
    "fee": fields.String(required=True, description="手续费", example="3.44"),
    "cost": fields.String(required=True, description="成本金额", example="2.00"),
    "profit": fields.String(required=True, description="收入金额", example="1.44")
})

deliver_info_deposit = api.model("deliver_info_deposit", {
    "channel_name": fields.String(required=True, description="通道", example="立马付"),
    "mch_id": fields.String(required=True, description="通道商户号", example="61135"),
    "channel_tx_id": fields.String(required=True, description="通道订单号", example="453432345")
})

DepositOrderDetail = api.model('DepositOrderDetail', {
    'detail_head': fields.Nested(DepositOrderItemHead),
    'order_merchant_info': fields.Nested(order_merchant_info_deposit),
    'deliver_info': fields.Nested(deliver_info_deposit),
    'user_info': fields.Nested(user_info),
    'event_log_list': fields.List(fields.Nested(event_log_list))
})

DescValuePair = api.model("DescValuePair", {
    "desc": fields.String(
        description="支付方式描述",
        example=PayMethodEnum.WEIXIN_H5.desc,
    ),
    "value": fields.String(
        description='支付方式数值',
        example=PayMethodEnum.WEIXIN_H5.value,
    ),
})


class DepositOrderDetailResult(ResponseSuccess):
    data_model = DepositOrderDetail


BackOfficeConfigDetail = api.model('BackOfficeConfigDetail', {
    'merchant': fields.List(fields.Nested(DescValuePair)),
    'payment_type': fields.List(fields.Nested(DescValuePair)),
    'deposit_channel': fields.List(fields.Nested(DescValuePair))
})


class BackOfficeConfigResult(ResponseSuccess):
    data_model = BackOfficeConfigDetail


######################################################
# 订单通知
######################################################
OrderStateNotifyDoc = api.model("OrderStateNotifyDoc", {
    "order_id": fields.Integer(
        required=True,
        description='订单号',
        example=11111,
    ),
    "order_type": fields.Integer(
        required=True,
        description='订单类型',
        example=PayTypeEnum.description_name_desc(values=[PayTypeEnum.DEPOSIT, PayTypeEnum.WITHDRAW]),
    ),
})
