import re
from decimal import Decimal

from wtforms import StringField, FieldList, FormField, Form, IntegerField
from wtforms.validators import DataRequired, StopValidation, length

from app.enums.channel import ChannelConfigEnum
from app.enums.trade import OrderStateEnum, PaymentBankEnum, CostTypeEnum, PayTypeEnum
from app.libs.balance_kit import BalanceKit
from app.libs.datetime_kit import DateTimeKit, DateTimeFormatEnum
from app.models.merchant import MerchantInfo, PayMethodEnum, MerchantTypeEnum, \
    PaymentFeeTypeEnum
from app.forms.base_form import BaseForm, stop_validate_if_error_occurred
from config import MerchantEnum
from app.enums.trade import PaymentTypeEnum


class OrderIdForm(BaseForm):
    order_id = StringField(
        description="订单号",
        validators=[DataRequired()],
    )


class OrderIdCommentForm(OrderIdForm):
    comment = StringField(
        description="备注信息",
        validators=[
            DataRequired(message="备注信息必填"),
            length(min=5, max=100, message="备注信息最小5个字符，最大30个字符"),
        ],
    )


################################################
# 编辑费率表单
################################################


class DepositForm(BaseForm):
    """
    充值信息
    """
    name = IntegerField(
        validators=[DataRequired()],
        description="充值方式"
    )

    value = StringField(
        validators=[DataRequired()],
        description="费率"
    )

    fee_type = IntegerField(
        validators=[DataRequired()],
        description="计费方式",
        default=PaymentFeeTypeEnum.PERCENT_PER_ORDER.value,
    )

    @stop_validate_if_error_occurred
    def validate_name(self, value):
        try:
            self.name.data = PayMethodEnum(int(value.data))
        except Exception as e:
            raise StopValidation("无效的支付方法")

    @stop_validate_if_error_occurred
    def validate_fee_type(self, value):
        try:
            self.fee_type.data = PaymentFeeTypeEnum(int(value.data))
        except Exception as e:
            raise StopValidation("无效的费率扣除方式")


class EditWithDrawForm(Form):
    """
    编辑提现费率配置
    """
    value = StringField(
        validators=[DataRequired(message="value 是必填字段")],
        description="提现费率",
    )

    fee_type = IntegerField(
        validators=[DataRequired(message="fee_type 是必填字段")],
        description="费率类型",
    )

    cost_type = StringField(
        validators=[DataRequired(message="cost_type 是必填字段")],
        description="扣费类型",
    )

    @stop_validate_if_error_occurred
    def validate_fee_type(self, value):
        try:
            self.fee_type.data = PaymentFeeTypeEnum(int(value.data))
        except Exception as e:
            raise StopValidation("无效的 fee_type")

    @stop_validate_if_error_occurred
    def validate_cost_type(self, value):
        try:
            self.cost_type.data = CostTypeEnum.from_name(value.data)
        except Exception as e:
            raise StopValidation("无效的 cost_type")


class EditMerchantRateForm(BaseForm):
    """
    描述文档: 编辑费率
    """
    name = StringField(validators=[
        DataRequired()],
        description="商户名称"
    )
    deposit_info = FieldList(FormField(DepositForm))
    withdraw_info = FormField(EditWithDrawForm)

    @stop_validate_if_error_occurred
    def validate_name(self, value):
        try:
            self.name.data = MerchantEnum.from_name(value.data.upper())
        except Exception as e:
            raise StopValidation("无效的商户名称")

        if not MerchantInfo.query_merchant(self.name.data):
            raise StopValidation("未创建的商户")


#####################################################
# 新增商户费率表单
#####################################################

class DomainForm(BaseForm):
    domain = StringField(
        validators=[DataRequired()],
        description="域名信息"
    )


class MerchantFeeAddForm(BaseForm):
    """
    运营在新增商户时，配置商户的基本信息表单
    """
    name = StringField(validators=[DataRequired()], description="商户名称")
    type = IntegerField(validators=[DataRequired()], description="商户类型")
    deposit_info = FieldList(FormField(DepositForm))
    withdraw_info = FormField(EditWithDrawForm)

    @stop_validate_if_error_occurred
    def validate_name(self, value):
        try:
            self.name.data = MerchantEnum.from_name(value.data.upper())
        except Exception as e:
            raise StopValidation("无效的商户名称")

    @stop_validate_if_error_occurred
    def validate_type(self, value):
        try:
            self.type.data = MerchantTypeEnum(int(value.data))
        except Exception as e:
            raise StopValidation("无效的商户类型")


#####################################################
# 提现订单管理 列表
#####################################################


class WithDrawSelectResultForm(BaseForm):
    """
    运营在新增商户时，配置商户的基本信息表单
    """
    order_id = StringField(description="商户订单号/系统订单号", default="")
    merchant_name = StringField(validators=[], description="商户名称")
    channel = StringField(validators=[], description="通道名称")
    page_size = IntegerField(validators=[DataRequired()], description="单页数据条数")
    page_index = IntegerField(validators=[DataRequired()], description="页码")
    begin_time = StringField(validators=[DataRequired()], description="开始时间", default="")
    end_time = StringField(validators=[DataRequired()], description="结束时间", default="")
    state = StringField(validators=[DataRequired()], default="0", description="充值订单状态")
    done_begin_time = StringField(description="开始时间(订单完成时间)", default="")
    done_end_time = StringField(description="结束时间(订单完成时间)", default="")

    @stop_validate_if_error_occurred
    def validate_channel(self, value):
        try:
            if value.data:
                self.channel.data = ChannelConfigEnum.from_name(value.data)
            else:
                self.channel.data = None
        except Exception as e:
            raise StopValidation("无效的channel")

    @stop_validate_if_error_occurred
    def validate_done_begin_time(self, value):
        try:
            if value.data:
                self.done_begin_time.data = DateTimeKit.str_to_datetime(value.data, DateTimeFormatEnum.SECONDS_FORMAT)
        except Exception as e:
            raise StopValidation("时间格式不对 精确到秒")

    @stop_validate_if_error_occurred
    def validate_done_end_time(self, value):
        try:
            if value.data:
                self.done_end_time.data = DateTimeKit.str_to_datetime(value.data, DateTimeFormatEnum.SECONDS_FORMAT)
        except Exception as e:
            raise StopValidation("时间格式不对 精确到秒")

    @stop_validate_if_error_occurred
    def validate_page_size(self, value):
        try:
            if not isinstance(value.data, int):
                raise StopValidation("无效的数据类型")
            if value.data == 0:
                raise StopValidation("单页条数不能为0")
            self.page_size.data = value.data
        except Exception as e:
            raise StopValidation("无效的数据条数")

    @stop_validate_if_error_occurred
    def validate_page_index(self, value):
        try:
            if not isinstance(value.data, int):
                raise StopValidation("无效的数据类型")
            if value.data == 0:
                raise StopValidation("页码不能为 0")
            self.page_index.data = value.data
        except Exception as e:
            raise StopValidation("无效的页码")

    @stop_validate_if_error_occurred
    def validate_merchant_name(self, value):
        try:
            if value.data:
                self.merchant_name.data = MerchantEnum.from_name(value.data)
            else:
                self.merchant_name.data = None
        except Exception as e:
            raise StopValidation("无效的商户名称")

    @stop_validate_if_error_occurred
    def validate_state(self, value):
        try:
            if value.data == "0":
                self.state.data = "0"
            else:
                self.state.data = OrderStateEnum(int(value.data))
        except Exception as e:
            raise StopValidation("无效的订单状态")

    @stop_validate_if_error_occurred
    def validate_begin_time(self, value):
        try:
            self.begin_time.data = DateTimeKit.str_to_datetime(value.data, DateTimeFormatEnum.SECONDS_FORMAT)
        except Exception as e:
            raise StopValidation("时间格式不对 精确到秒")

    @stop_validate_if_error_occurred
    def validate_end_time(self, value):
        try:
            self.end_time.data = DateTimeKit.str_to_datetime(value.data, DateTimeFormatEnum.SECONDS_FORMAT)
        except Exception as e:
            raise StopValidation("时间格式不对 精确到秒")


class WithDrawOrderAllowedForm(BaseForm):
    """
    运营 认领提现订单
    """
    order_id = StringField(description="系统订单号")
    merchant_name = StringField(validators=[DataRequired()], description="商户名称")

    def validate_merchant_name(self, value):
        try:
            self.merchant_name.data = MerchantEnum.from_name(value.data.upper())
        except Exception as e:
            raise StopValidation("无效的商户名称")


class WithdrawOrderPerformForm(BaseForm):
    """
    运营确认出款
    """
    merchant = StringField(validators=[DataRequired()], description="商户名称")
    order_id = StringField(validators=[DataRequired()], description="订单ID")
    channel_id = StringField(validators=[DataRequired()], description="通道ID")

    def validate_merchant(self, value):
        try:
            self.merchant.data = MerchantEnum.from_name(value.data)
        except Exception as e:
            raise StopValidation("无效的商户名称")


##################################################
# 运营代付
##################################################

class ExecuteWithDrawOrderForm(BaseForm):
    """
    运营 认领提现订单
    """
    order_id = StringField(validators=[DataRequired()], description="系统订单号")
    merchant_name = StringField(validators=[DataRequired()], description="商户名称")
    channel_id = StringField(validators=[DataRequired()], description="代付通道")

    def validate_merchant_name(self, value):
        try:
            self.merchant_name.data = MerchantEnum.from_name(value.data.upper())
        except Exception as e:
            raise StopValidation("无效的商户名称")

    def validate_channel_id(self, value):
        try:
            self.channel_id.data = ChannelConfigEnum(int(value.data))
        except Exception as e:
            raise StopValidation("无效的代付通道")


class WithDrawSupperBankForm(BaseForm):
    """
    运营 认领提现订单
    """
    bank_type = StringField(validators=[DataRequired()], description="银行类型")
    merchant_name = StringField(validators=[DataRequired()], description="商户名称")
    amount = StringField(validators=[DataRequired()], description="提现金额")

    def validate_merchant_name(self, value):
        try:
            self.merchant_name.data = MerchantEnum.from_name(value.data)
        except Exception as e:
            raise StopValidation("无效的 merchant_name")

    def validate_bank_type(self, value):
        try:
            self.bank_type.data = PaymentBankEnum.from_name(value.data)
        except Exception as e:
            raise StopValidation("无效的 bank_type")

    def validate_amount(self, value):
        try:
            self.amount.data = Decimal(value.data)
        except Exception as e:
            raise StopValidation("无效的 amount")


#########################################################################
# 提现订单详情
#########################################################################

class WithDrawOrderDetailForm(BaseForm):
    """
    运营 认领提现订单
    """
    order_id = StringField(validators=[DataRequired()], description="系统订单Id")


#########################################################################
# 提现用户银行信息查询
#########################################################################

class WithDrawBankForm(BaseForm):
    """
    运营 认领提现订单
    """
    order_id = StringField(validators=[DataRequired()], description="订单Id")
    merchant = StringField(validators=[DataRequired()], description="商户名")

    def validate_merchant(self, value):
        try:
            self.merchant.data = MerchantEnum.from_name(value.data.upper())
        except Exception as e:
            raise StopValidation("无效的商户名称")


#########################################################################
# 手工提现 出款完成
#########################################################################

class WithDrawPersonExecutedDoneForm(BaseForm):
    """
    运营 认领提现订单
    """
    order_id = StringField(validators=[DataRequired()], description="订单Id")
    merchant = StringField(validators=[DataRequired()], description="商户名")
    comment = StringField(validators=[DataRequired()], description="附加信息")
    fee = StringField(default="0", description="手续费")

    def validate_merchant(self, value):
        try:
            self.merchant.data = MerchantEnum.from_name(value.data.upper())
        except Exception as e:
            raise StopValidation("无效的商户名称")


#######################################################
# 审核
#######################################################
class YearMouthForm(BaseForm):
    """
    运营确认出款
    """
    year = StringField(validators=[DataRequired()], description="年")
    mouth = StringField(validators=[DataRequired()], description="月")

    # def validate_year(self, value):
    #     if re.match('^2[0, 1]\d{2}', value.data.encode('utf8')):
    #         self.year.data = value.data
    #     else:
    #         raise StopValidation("无效的年份")
    #
    # def validate_mouth(self, value):
    #     value.data = value.data.encode('utf8')
    #     if re.match('^\d$', value.data) or re.match('^1[0, 1, 2]$', value.data) or re.match('^0\d$', value.data):
    #         self.mouth.data = value.data
    #     else:
    #         raise StopValidation("无效的月份")


#####################################################
# 充值订单管理 列表
#####################################################


class DepositOrderListSelectResultForm(BaseForm):
    """
    运营在新增商户时，配置商户的基本信息表单
    """
    order_id = StringField(description="商户订单号/系统订单号", default="")
    merchant_name = StringField(validators=[], description="商户名称")
    channel = StringField(validators=[], description="通道名称")
    page_size = IntegerField(validators=[DataRequired()], description="单页数据条数")
    page_index = IntegerField(validators=[DataRequired()], description="页码")
    begin_time = StringField(validators=[DataRequired()], description="开始时间", default="")
    end_time = StringField(validators=[DataRequired()], description="结束时间", default="")
    state = StringField(validators=[DataRequired()], default="0", description=OrderStateEnum.description())
    done_begin_time = StringField(description="开始时间(订单完成时间)", default="")
    done_end_time = StringField(description="结束时间(订单完成时间)", default="")

    @stop_validate_if_error_occurred
    def validate_channel(self, value):
        try:
            if value.data:
                self.channel.data = ChannelConfigEnum.from_name(value.data)
            else:
                self.channel.data = None
        except Exception as e:
            raise StopValidation("无效的channel")

    @stop_validate_if_error_occurred
    def validate_done_begin_time(self, value):
        try:
            if value.data:
                self.done_begin_time.data = DateTimeKit.str_to_datetime(value.data, DateTimeFormatEnum.SECONDS_FORMAT)
        except Exception as e:
            raise StopValidation("时间格式不对 精确到秒")

    @stop_validate_if_error_occurred
    def validate_done_end_time(self, value):
        try:
            if value.data:
                self.done_end_time.data = DateTimeKit.str_to_datetime(value.data, DateTimeFormatEnum.SECONDS_FORMAT)
        except Exception as e:
            raise StopValidation("时间格式不对 精确到秒")

    @stop_validate_if_error_occurred
    def validate_page_size(self, value):
        try:
            if not isinstance(value.data, int):
                raise StopValidation("无效的数据类型")
            if value.data == 0:
                raise StopValidation("单页条数不能为0")
            self.page_size.data = value.data
        except Exception as e:
            raise StopValidation("无效的数据条数")

    @stop_validate_if_error_occurred
    def validate_page_index(self, value):
        try:
            if not isinstance(value.data, int):
                raise StopValidation("无效的数据类型")
            if value.data == 0:
                raise StopValidation("页码不能为 0")
            self.page_index.data = value.data
        except Exception as e:
            raise StopValidation("无效的页码")

    @stop_validate_if_error_occurred
    def validate_merchant_name(self, value):
        try:
            if value.data:
                self.merchant_name.data = MerchantEnum.from_name(value.data)
            else:
                self.merchant_name.data = None
        except Exception as e:
            raise StopValidation("无效的商户名称")

    @stop_validate_if_error_occurred
    def validate_state(self, value):
        try:
            if value.data == "0":
                self.state.data = "0"
            else:
                self.state.data = OrderStateEnum(int(value.data))
        except Exception as e:
            raise StopValidation("无效的订单状态")

    @stop_validate_if_error_occurred
    def validate_begin_time(self, value):
        try:
            self.begin_time.data = DateTimeKit.str_to_datetime(value.data, DateTimeFormatEnum.SECONDS_FORMAT)
        except Exception as e:
            raise StopValidation("时间格式不对 精确到秒")

    @stop_validate_if_error_occurred
    def validate_end_time(self, value):
        try:
            self.end_time.data = DateTimeKit.str_to_datetime(value.data, DateTimeFormatEnum.SECONDS_FORMAT)
        except Exception as e:
            raise StopValidation("时间格式不对 精确到秒")


#########################################################################
# 手动补单表单验证
#########################################################################

class CreateDepositOrderForm(BaseForm):
    """
    手动补单
    """
    uid = StringField(validators=[DataRequired()], description="用户id")
    merchant = StringField(validators=[DataRequired()], description="商户名")
    payment_type = StringField(validators=[DataRequired()], description="支付方式")
    channel_id = StringField(validators=[DataRequired()], description="通道id")
    mch_tx_id = StringField(validators=[DataRequired()], description="通道订单号")
    amount = StringField(validators=[DataRequired()], description="金额")
    remark = StringField(validators=[DataRequired()], description="备注")

    @stop_validate_if_error_occurred
    def validate_amount(self, value):
        try:
            self.amount.data = Decimal(value.data)
            BalanceKit.multiple_hundred(self.amount.data)
        except Exception as e:
            raise StopValidation("无效的 amount，必须是整数或浮点数字符串，最多保留2位小数")

    @stop_validate_if_error_occurred
    def validate_merchant(self, value):
        try:
            self.merchant.data = MerchantEnum.from_name(value.data.upper())
        except Exception as e:
            raise StopValidation("无效的商户名称")

    @stop_validate_if_error_occurred
    def validate_payment_type(self, value):
        try:
            self.payment_type.data = PaymentTypeEnum(int(value.data))
        except Exception as e:
            raise StopValidation("无效的支付方式")

    @stop_validate_if_error_occurred
    def validate_channel_id(self, value):
        try:
            self.channel_id.data = ChannelConfigEnum(int(value.data))
        except Exception as e:
            raise StopValidation("无效的通道")


#########################################################################
# 订单通知
#########################################################################

class OrderStateNotifyFrom(BaseForm):
    """
    订单通知
    """
    order_id = StringField(validators=[DataRequired()], description="订单Id")
    order_type = StringField(validators=[DataRequired()], description="订单类型")

    @stop_validate_if_error_occurred
    def validate_order_id(self, value):
        try:
            self.order_id.data = int(value.data)
        except Exception as e:
            raise StopValidation("无效的 order_id")

    @stop_validate_if_error_occurred
    def validate_order_type(self, value):
        try:
            self.order_type.data = PayTypeEnum.from_name(value.data)
        except Exception as e:
            raise StopValidation("无效的 order_id")
