from flask_restplus import fields

from app.enums.channel import ChannelStateEnum
from app.extensions.ext_api import api_backoffice as api

from app.libs.error_code import ResponseSuccess
from app.enums.trade import PayMethodEnum, PaymentTypeEnum, PaymentFeeTypeEnum, SettleTypeEnum, PaymentBankEnum, \
    InterfaceTypeEnum, PayTypeEnum
from config import MerchantEnum

DescNamePair = api.model("DescNamePair", {
    "name": fields.String(),
    "desc": fields.String()
})

ChannelConfigQueryDoc = api.model('DocChannelConfigQuery', {
    "pay_type": fields.Integer(
        required=True,
        description='通道号',
        example=PayTypeEnum.description()
    ),
})

bank = fields.String(
    required=True,
    description='支持的银行',
    example=PaymentBankEnum.description()
)

payment_methods = fields.String(
    required=True,
    description='支付方法',
    example=PayMethodEnum.description()
)

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

maintain_datetime = api.model('maintain_datetime', {
    "maintain_begin": fields.String(
        description='维护开始时间',
        example="2019-09-27 09:00:00"
    ),
    "maintain_end": fields.String(
        description='维护结束时间',
        example="2019-10-20 23:00:00"
    ),
})

trade_end_time = api.model('trade_end_time', {
    "trade_end_hour": fields.String(
        required=True,
        description='交易时间',
        example="21"
    ),
    "trade_end_minute": fields.String(
        required=True,
        description='交易时间',
        example="05"
    ),
})

trade_start_time = api.model('trade_start_time', {
    "trade_begin_hour": fields.String(
        required=True,
        description='交易时间',
        example="08"
    ),
    "trade_begin_minute": fields.String(
        required=True,
        description='交易时间',
        example="00"
    ),
})

NameValuePair = api.model("NameValuePair", {
    "key": fields.String(required=True, description="Id"),
    "value": fields.String(required=True, description="name")
})

ChannelItem = api.model('ChannelItem', {
    "channel_id": fields.Integer(required=True, description="通道Id"),
    "channel_desc": fields.String(required=True, description="通道描述"),
    "id": fields.String(required=True, description="商户号"),
    "provider": fields.String(required=True, description='支付公司'),
    "name": fields.String(required=True, description='渠道名称'),
    "payment_type": fields.Nested(DescValuePair),
    "payment_method": fields.Nested(DescValuePair),
    "fee": fields.String(required=True, description='成本费率'),
    "fee_type": fields.Nested(DescValuePair),
    "limit_per_min": fields.String(required=True, description='单笔交易下限'),
    "limit_per_max": fields.String(required=True, description='单笔交易上限'),
    "limit_day_max": fields.String(required=True, description='日交易限额'),
    "settlement_type": fields.Nested(NameValuePair),
    "trade_start_time": fields.String(required=True, description='交易开始时间'),
    "trade_end_time": fields.String(required=True, description='交易结束时间'),
    "main_time": fields.Nested(maintain_datetime),
    "state": fields.Nested(DescValuePair, description="可操作类型列表"),
    "reason": fields.String(required=True, description='不可用原因'),
    "priority": fields.String(required=True, description='优先级'),
    "merchants": fields.List(
        fields.String,
        required=True,
        description='适用的商户列表',
        example=MerchantEnum.get_names(),
    ),
})

ChannelList = api.model('ChannelList', {
    'counts': fields.String(
        required=True,
        description='渠道总个数',
        example="10"
    ),
    'channels': fields.List(fields.Nested(ChannelItem)),
})


class ChannelListResult(ResponseSuccess):
    data_model = ChannelList


######################################################
# 新增 渠道
######################################################

limiter_per = api.model('limiter_per', {
    "limit_per_min": fields.String(
        required=True,
        description='单笔交易下限',
        example="2000"
    ),
    "limit_per_max": fields.String(
        required=True,
        description='单笔交易上限',
        example="30000"
    ),
})

trade_time = api.model('trade_time', {
    "trade_begin": fields.String(
        required=True,
        description='每日交易开始时间',
        example="09：00"
    ),
    "trade_end": fields.String(
        required=True,
        description='每日交易结束时间',
        example="23：00"
    )
})

ChannelAddList = api.model('ChannelAddList', {
    "channel_id": fields.Integer(
        required=True,
        description='通道号',
        example=101
    ),
    'fee': fields.String(
        required=True,
        description='成本',
        example="2.3"
    ),
    'fee_type': fields.String(
        required=True,
        description='费用类型',
        example="1"
    ),
    'limit_per_min': fields.String(
        required=True,
        description='单笔交易下限',
        example="2000"
    ),
    'limit_per_max': fields.String(
        required=True,
        description='单笔交易上限',
        example="50000"
    ),
    # 'limiter_per': fields.Nested(limiter_per),
    'limit_day_max': fields.String(
        required=True,
        description='日交易限额',
        example="50000"
    ),
    "start_time": fields.String(
        required=True,
        description='每日交易开始时间',
        example="09:00"
    ),
    "end_time": fields.String(
        required=True,
        description='每日交易结束时间',
        example="23:00"
    ),
    "maintain_begin": fields.String(
        description='维护开始时间',
        example="2019-09-27 09:00:00"
    ),
    "maintain_end": fields.String(
        description='维护结束时间',
        example="2019-10-20 23:00:00"
    ),
    "state": fields.String(
        required=True,
        description='账户状态',
        example=ChannelStateEnum.description()
    ),
    "settlement_type": fields.String(
        required=True,
        description='结算方式',
        example=SettleTypeEnum.description()
    ),
    "priority": fields.String(
        required=True,
        description='优先级',
        example="1"
    )
})

#############################################################
# 获取通道配置信息
#############################################################

channel_config = api.model("channel_config", {
    "channel_id": fields.Integer(
        required=True,
        description='通道号',
        example=101
    ),
    "channel_desc": fields.String(
        required=True,
        description='通道描述',
    ),
    'id': fields.String(
        required=True,
        description='渠道商户号',
        example="WX101"
    ),
    'provider': fields.String(
        required=True,
        description='支付公司',
        example="腾讯"
    ),
    'name': fields.String(
        required=True,
        description='渠道',
        example="微信网页支付"
    ),
    'payment_type': fields.String(
        required=True,
        description='支付类型',
        example=PaymentTypeEnum.description()
    ),
    'payment_method': fields.String(
        required=True,
        description='支付方法',
        example=PayMethodEnum.description()
    )
})

NameValuePair = api.model("NameValuePair", {
    "name": fields.String(
        description="支付方式描述",
        example=PayMethodEnum.WEIXIN_H5.desc,
    ),
    "value": fields.String(
        description='支付方式数值',
        example=PayMethodEnum.WEIXIN_H5.value,
    ),
})

ChannelConfigInfo = api.model("ChannelConfigInfo", {
    "channel_config": fields.List(fields.Nested(channel_config), description="通道基本配置信息"),
    # "payment_method": fields.List(fields.Nested(DescValuePair), description="支付方式列表"),
    # "payment_type": fields.List(fields.Nested(DescValuePair), description="支付大类列表"),
    "payment_fee_type": fields.List(fields.Nested(DescValuePair), description="费率扣除方式"),
    "settlement_type": fields.List(fields.Nested(NameValuePair), description="结算方式"),
    "channel_state": fields.List(fields.Nested(DescValuePair), description="通道状态"),
    "banks": fields.List(fields.Nested(DescValuePair), description="银行列表"),
    # "banks": fields.List(bank),
    "interfaces": fields.List(fields.Nested(NameValuePair), description="接入类型"),
    "payment_method": fields.List(fields.Nested(DescValuePair), description="支付方法"),
    "merchant_name": fields.List(fields.Nested(NameValuePair), description="商户列表"),
    "payment_types": fields.List(fields.Nested(DescNamePair), description="支付类型列表"),
})


class ChannelConfigResult(ResponseSuccess):
    data_model = ChannelConfigInfo


###########################################################
# 代付通道 新增代付通道
###########################################################


WithdrawAddList = api.model('WithdrawAddList', {
    "channel_id": fields.Integer(
        required=True,
        description='通道号',
        example=101
    ),
    'id': fields.String(
        required=True,
        description='渠道商户号',
        example="WX101"
    ),
    'fee': fields.String(
        required=True,
        description='成本费率',
        example="2.3"
    ),
    'fee_type': fields.String(
        required=True,
        description='费用类型',
        example=PaymentFeeTypeEnum.description(),
    ),
    'limit_per_min': fields.String(
        required=True,
        description='单笔交易下限',
        example="2000"
    ),
    'limit_per_max': fields.String(
        required=True,
        description='单笔交易上限',
        example="50000"
    ),
    'limit_day_max': fields.String(
        description='日交易限额',
        example="50000"
    ),
    "start_time": fields.String(
        required=True,
        description='每日交易开始时间',
        example="09:00"
    ),
    "end_time": fields.String(
        required=True,
        description='每日交易结束时间',
        example="23:00"
    ),
    "maintain_begin": fields.String(
        description='维护开始时间',
        example="2019-09-27 09:00:00"
    ),
    "maintain_end": fields.String(
        description='维护结束时间',
        example="2019-10-20 23:00:00"
    ),
    "state": fields.String(
        required=True,
        description='账户状态',
        example=ChannelStateEnum.description()
    ),
    "banks": fields.List(bank)
})

#############################################################
WithdrawItem = api.model('WithdrawItem', {
    "channel_id": fields.Integer(required=True, description="通道Id"),
    "channel_desc": fields.String(required=True, description="通道描述"),
    "id": fields.String(required=True, description="代付通道商户号"),
    "provider": fields.String(required=True, description='支付公司'),
    "name": fields.String(required=True, description='渠道名称'),
    "fee": fields.String(required=True, description='成本费率'),
    "fee_type": fields.Nested(DescValuePair),
    "limit_per_min": fields.String(required=True, description='单笔交易下限'),
    "limit_per_max": fields.String(required=True, description='单笔交易上限'),
    "limit_day_max": fields.String(required=True, description='日交易限额'),
    "trade_start_time": fields.String(required=True, description='交易开始时间'),
    "trade_end_time": fields.String(required=True, description='交易结束时间'),
    "main_time": fields.Nested(maintain_datetime),
    "state": fields.Nested(DescValuePair, description="可操作类型列表"),
    "reason": fields.String(required=True, description='不可用原因'),
    "banks": fields.List(bank)
})

WithdrawList = api.model('ChannelList', {
    'counts': fields.String(
        required=True,
        description='代付渠道总个数',
        example="10"
    ),
    'withdraws': fields.List(fields.Nested(WithdrawItem)),
})


class WithdrawListResult(ResponseSuccess):
    data_model = WithdrawList


#############################################
# 引导规则 拉取引导规则
#############################################

##############################################################
# 输出方案
##############################################################
ConfigItem = api.model("ConfigItem", dict(
    payment_type=fields.String(
        required=True,
        description=PaymentTypeEnum.description_name_desc(),
        example=PaymentTypeEnum.ZHIFUBAO.name,
    ),
    priority=fields.Integer(
        required=True,
        description='优先级',
        example=100
    ),
))

RuleItem = api.model('RuleItem', {
    "router_id": fields.Integer(
        description="引导编号",
    ),
    "config_list": fields.List(
        fields.Nested(ConfigItem),
        description="输出方案",
    ),
    'interface': fields.Nested(
        DescNamePair,
        description="接入类型",
    ),
    'amount_min': fields.String(
        description='交易金额最小值',
        example="5000.00"
    ),
    'amount_max': fields.String(
        description='交易金额最大值',
        example="10000.00"
    ),
    'merchants': fields.List(fields.String(
        description=MerchantEnum.description_name_desc(),
        example=MerchantEnum.TEST.name,
    )),
    'uid_list': fields.List(fields.Integer(
        description='用户ID',
        example=1,
    )),
    "create_time": fields.String(
        description="创建时间",
    )
})

RuleList = api.model('RuleList', {
    'counts': fields.Integer(
        required=True,
        description='引导规则总个数',
        example=10
    ),
    'rules': fields.List(fields.Nested(RuleItem)),
})


class RuleListResult(ResponseSuccess):
    data_model = RuleList


RouterCondition = api.model('RouterCondition', {
    'interface': fields.String(
        description=InterfaceTypeEnum.description_name_desc(),
        example=InterfaceTypeEnum.CASHIER_H5.name,
    ),
    'amount_min': fields.Integer(
        description='交易金额最小值',
        example="5000.99"
    ),
    'amount_max': fields.Integer(
        description='交易金额最大值',
        example="50000.33"
    ),
    'merchants': fields.List(
        fields.String(),
        description=MerchantEnum.description_name_desc(),
        example=[MerchantEnum.TEST.name, MerchantEnum.QF2.name],
    ),
    'uid_list': fields.List(
        fields.Integer(),
        description='用户ID列表',
        example=[1, 2, 3],
    ),
})

RuleAddList = api.inherit('RuleAddList', RouterCondition, {
    "config_list": fields.List(
        fields.Nested(ConfigItem),
        required=True,
        description="输出方案",
    ),
})

RuleEditList = api.inherit('RuleEditList', RouterCondition, {
    "router_id": fields.Integer(
        required=True,
        description='路由id',
        example=1
    ),
    "config_list": fields.List(
        fields.Nested(ConfigItem),
        description="输出方案",
    ),
})

RouterAddDoc = api.inherit('RouterAddDoc', RouterCondition, {
    "channel": fields.Integer(
        required=True,
        description="通道ID",
    ),
})
