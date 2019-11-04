from app.enums.trade import BalanceAdjustTypeEnum, PayMethodEnum, OrderStateEnum, PayTypeEnum
from app.extensions.ext_api import api_backoffice as api
from flask_restplus import fields

#################################
# user list select
#################################
from app.libs.error_code import ResponseSuccess

UserList = api.model("UserList", {
    "phone_number": fields.String(
        description='手机号码',
        example="+8618912341234"
    ),
    "start_datetime": fields.String(
        description='注册开始查询时间',
        example="2019-09-12 08:12:23"
    ),
    "end_datetime": fields.String(
        description='注册结束查询时间',
        example="2019-09-19 23:12:23"
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
})

##############################
# 用户数据展示
##############################

UserItem = api.model('UserItem', {
    'user_id': fields.String(required=True, description="用户Id", example="12"),
    'phone_number': fields.String(required=True, description="手机号", example="133****5497"),
    'type': fields.String(required=True, description="用户类型", example="测试用户/普通用户"),
    'source': fields.String(required=True, description="用户涞源", example="用户涞源"),
    "available_bl": fields.String(required=True, description="可用金币", example="1000"),
    "register_datetime": fields.String(required=True, description="注册时间", example="2019-09-12 08:17:22"),
    "state": fields.String(required=True, description="用户状态", example="正常/禁止提现")
})

UserListMode = api.model('UserListMode', {
    'entries': fields.List(fields.Nested(UserItem)),
    'total': fields.String(
        required=True, description="总条数", example="518"
    )
})


class UserListResult(ResponseSuccess):
    data_model = UserListMode


###############################
# 用户信息查询
###############################

UserInfo = api.model('UserInfo', {
    'uid': fields.String(required=True, description="用户Id", example="10")
})

###############################
# 用户最近一周交易记录
###############################

UserTransaction = api.model('UserTransaction', {
    'uid': fields.String(required=True, description="用户Id", example="10"),
    "pay_type": fields.String(required=True, description="交易类型", example=PayTypeEnum.description()),
    'page_size': fields.Integer(
        required=True,
        description='单页数据条数',
        example=10,
    ),
    'page_index': fields.Integer(
        required=True,
        description='页码',
        example=1,
    )
})

###############################
# 用户余额调整
###############################

UserBalanceEditApi = api.model("UserBalanceEditApi", {
    "uid": fields.String(required=True, description="用户Id", example="10"),
    "adjust_type": fields.String(required=True, description="余额调整类型", example=""),
    "amount": fields.String(required=True, description="调整金额", example="500.00"),
    "comment": fields.String(required=True, description="备注", example="备注信息")
})

##############################
# 用户详细数据展示
##############################

BankCardItem = api.model('BankCardItem', {
    'bank_id': fields.String(required=True, description="银行卡id", example="1"),
    'bank_name': fields.String(required=True, description="银行名称", example="中国工商银行"),
    'account_name': fields.String(required=True, description="持卡人姓名", example="张三"),
    'card_no': fields.String(required=True, description="银行卡号", example="**** **** **** 1234"),
    'province': fields.String(required=True, description="开户地区", example="广东省/深圳市"),
    "branch": fields.String(required=True, description="开户支行名称", example="罗湖支行")
})

HeadInfo = api.model('HeadInfo', {
    'uid': fields.String(required=True, description="用户Id", example="12"),
    'account': fields.String(required=True, description="手机号", example="133****5497"),
    'type': fields.String(required=True, description="用户类型", example="测试用户/普通用户"),
    'source': fields.String(required=True, description="用户涞源", example="用户涞源"),
    "ava_bl": fields.String(required=True, description="可用金币", example="1000"),
    "create_time": fields.String(required=True, description="注册时间", example="2019-09-12 08:17:22"),
    "state": fields.String(required=True, description="用户状态", example="正常/禁止提现")
})

UserEntriesDetailMode = api.model('UserEntriesDetailMode', {
    'headInfo': fields.Nested(HeadInfo),
    'bankcardEntries': fields.List(fields.Nested(BankCardItem))
})


class UserEntriesDetailResult(ResponseSuccess):
    data_model = UserEntriesDetailMode


####################################################
# 用户最近一周交易 充值订单查询结果
####################################################

DepositItem = api.model("DepositItem", {
    "mch_tx_id": fields.String(required=True, description="商户订单号", example="PN20190328123344444404444"),
    "sys_tx_id": fields.String(required=True, description="系统订单号", example="201903291338464873929024"),
    "pay_method": fields.String(required=True, description="支付方法", example=PayMethodEnum.description()),
    "amount": fields.String(required=True, description="发起金额", example="500"),
    "tx_amount": fields.String(required=True, description="实际支付金额", example="499.98"),
    "create_time": fields.String(required=True, description="创建时间", example="2019-09-27 08:03:45"),
    "state": fields.String(required=True, description="订单状态", example=OrderStateEnum.description())

})

WithdrawItem = api.model("WithdrawItem", {
    "mch_tx_id": fields.String(required=True, description="商户订单号", example="PN20190328123344444404444"),
    "sys_tx_id": fields.String(required=True, description="系统订单号", example="201903291338464873929024"),
    "amount": fields.String(required=True, description="提现金额", example="500"),
    "fee": fields.String(required=True, description="手续费", example="3"),
    "bank_name": fields.String(required=True, description="银行名称", example="工商银行"),
    "card_no": fields.String(required=True, description="银行卡号", example="6228 4818 3904 0687 576"),
    "state": fields.String(required=True, description="订单状态", example=OrderStateEnum.description()),
    "create_time": fields.String(required=True, description="创建时间", example="2019-09-27 08:03:45"),
    "done_time": fields.String(required=True, description="完成时间", example="2019-09-27 08:03:45")
})

DepositInfo = api.model("DepositInfo", {
    "entries": fields.List(fields.Nested(DepositItem)),
    "total": fields.String(required=True, description="总条数", example="518")
})

WithdrawInfo = api.model("WithdrawInfo", {
    "entries": fields.List(fields.Nested(WithdrawItem)),
    "total": fields.String(required=True, description="总条数", example="518")
})

UserDepositMode = api.model("UserDepositMode", {
    "depositInfo": fields.Nested(DepositInfo),
    "withdrawInfo": fields.Nested(WithdrawInfo)
})


class UserDepositResult(ResponseSuccess):
    data_model = UserDepositMode


###########################
# 用户银行卡信息 编辑
###########################

UserBankInfo = api.model("UserBankInfo", {
    "card_id": fields.String(required=True, description="银行卡Id", example="10")
})
