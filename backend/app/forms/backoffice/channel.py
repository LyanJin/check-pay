from decimal import Decimal

from wtforms import StringField, Form, IntegerField, TimeField, FieldList
from wtforms.validators import DataRequired, StopValidation

from app.libs.balance_kit import BalanceKit
from app.libs.datetime_kit import DateTimeKit, DateTimeFormatEnum
from app.models.channel import PayMethodEnum, PaymentFeeTypeEnum
from app.forms.base_form import BaseForm, stop_validate_if_error_occurred
from app.enums.channel import ChannelStateEnum, ChannelConfigEnum
from app.enums.trade import SettleTypeEnum, InterfaceTypeEnum, PaymentBankEnum, PayTypeEnum, PaymentTypeEnum
from config import MerchantEnum
import datetime
from app.libs.custom_form import StringRequired, IntegerRequired


class ChannelConfigQueryForm(BaseForm):
    """
    运营在新增商户时，配置商户的基本信息表单
    """
    pay_type = IntegerField(validators=[DataRequired(), IntegerRequired()], description="通道类型")

    @stop_validate_if_error_occurred
    def validate_pay_type(self, value):
        try:
            self.pay_type.data = PayTypeEnum(value.data)
        except Exception as e:
            raise StopValidation("无效的pay_type")


################################################
# 通道管理： 新增通道
################################################

class LimiterPerForm(Form):
    """
    充值信息
    """
    per_min = StringField(
        validators=[DataRequired(), StringRequired()],
        description="每笔最低限额"
    )

    per_max = StringField(
        validators=[DataRequired(), StringRequired()],
        description="每笔最高限额"
    )


class TradeTimeForm(BaseForm):
    start_time = TimeField(
        validators=[DataRequired()],
        description="开始交易时间"
    )
    end_time = TimeField(
        validators=[DataRequired()],
        description="结束交易时间"
    )


class ChannelAddForm(BaseForm):
    """
    运营在新增商户时，配置商户的基本信息表单
    """
    channel_id = IntegerField(validators=[DataRequired(), IntegerRequired()], description="通道号")
    fee = StringField(validators=[DataRequired(), StringRequired()], description="成本费率")
    fee_type = StringField(validators=[DataRequired(), StringRequired()], description="费率类型")
    limit_per_min = StringField(validators=[DataRequired(), StringRequired()], description="每笔最低限额")
    limit_per_max = StringField(validators=[DataRequired(), StringRequired()], description="每笔最高限额")
    limit_day_max = StringField(description="日交易限额", default="")
    settlement_type = StringField(validators=[DataRequired(), StringRequired()], description="结算方式")
    start_time = StringField(validators=[DataRequired(), StringRequired()], description="开始交易时间")
    end_time = StringField(validators=[DataRequired(), StringRequired()], description="结束交易时间")
    maintain_begin = StringField(default="", description="维护开始时间")
    maintain_end = StringField(default="", description="维护结束时间")
    state = StringField(validators=[DataRequired(), StringRequired()], description="状态")
    priority = StringField(validators=[DataRequired(), StringRequired()], description="优先级")

    @stop_validate_if_error_occurred
    def validate_channel_id(self, value):
        try:
            self.channel_id.data = ChannelConfigEnum(int(value.data))
        except Exception as e:
            raise StopValidation("无效的渠道ID")

    @stop_validate_if_error_occurred
    def validate_state(self, value):
        try:
            self.state.data = ChannelStateEnum(int(value.data))
        except Exception as e:
            raise StopValidation("无效的通道状态")

    @stop_validate_if_error_occurred
    def validate_settlement_type(self, value):
        try:
            self.settlement_type.data = SettleTypeEnum(int(value.data))
        except Exception as e:
            raise StopValidation("无效的结算类型")

    @stop_validate_if_error_occurred
    def validate_fee_type(self, value):
        try:
            self.fee_type.data = PaymentFeeTypeEnum(int(value.data))
        except Exception as e:
            raise StopValidation("无效的费率扣除类型")

    @stop_validate_if_error_occurred
    def validate_maintain_begin(self, value):
        try:
            if value.data:
                self.maintain_begin.data = DateTimeKit.str_to_datetime(value.data)
        except Exception as e:
            raise StopValidation("无效的时间格式")

    @stop_validate_if_error_occurred
    def validate_maintain_end(self, value):
        try:
            if value.data:
                self.maintain_end.data = DateTimeKit.str_to_datetime(value.data)
        except Exception as e:
            raise StopValidation("无效的时间格式")

    @stop_validate_if_error_occurred
    def validate_start_time(self, value):
        try:
            self.start_time.data = DateTimeKit.str_to_datetime(value.data, DateTimeFormatEnum.HOURS_MINUTES_FORMAT)
        except Exception as e:
            raise StopValidation("无效的时间格式")

    @stop_validate_if_error_occurred
    def validate_end_time(self, value):
        try:
            self.end_time.data = DateTimeKit.str_to_datetime(value.data, DateTimeFormatEnum.HOURS_MINUTES_FORMAT)
        except Exception as e:
            raise StopValidation("无效的时间格式")


###############################################################
# 代付通道 新增代付通道
###############################################################

bank = StringField(validators=[DataRequired(), StringRequired()], description="支持的银行")


class WithdrawAddForm(BaseForm):
    """
    运营在新增商户时，配置商户的基本信息表单
    """
    channel_id = IntegerField(validators=[DataRequired(), IntegerRequired()], description="通道号")
    fee = StringField(validators=[DataRequired(), StringRequired()], description="成本费率")
    fee_type = StringField(validators=[DataRequired(), StringRequired()], description="费率类型")
    limit_per_min = StringField(validators=[DataRequired(), StringRequired()], description="每笔最低限额")
    limit_per_max = StringField(validators=[DataRequired(), StringRequired()], description="每笔最高限额")
    limit_day_max = StringField(description="日交易限额", default="")
    start_time = StringField(validators=[DataRequired(), StringRequired()], description="开始交易时间")
    end_time = StringField(validators=[DataRequired(), StringRequired()], description="结束交易时间")
    maintain_begin = StringField(default="", description="维护开始时间")
    maintain_end = StringField(default="", description="维护结束时间")
    state = StringField(validators=[DataRequired(), StringRequired()], description="状态")
    # banks = StringField(validators=[DataRequired(), StringRequired()], description="支持的银行")
    banks = FieldList(bank)

    @stop_validate_if_error_occurred
    def validate_channel_id(self, value):
        try:
            self.channel_id.data = ChannelConfigEnum(int(value.data))
        except Exception as e:
            raise StopValidation("无效的渠道ID")

    @stop_validate_if_error_occurred
    def validate_state(self, value):
        try:
            self.state.data = ChannelStateEnum(int(value.data))
        except Exception as e:
            raise StopValidation("无效的商户状态")

    @stop_validate_if_error_occurred
    def validate_settlement_type(self, value):
        try:
            self.settlement_type.data = SettleTypeEnum(int(value.data))
        except Exception as e:
            raise StopValidation("无效的结算类型")

    @stop_validate_if_error_occurred
    def validate_fee_type(self, value):
        try:
            self.fee_type.data = PaymentFeeTypeEnum(int(value.data))
        except Exception as e:
            raise StopValidation("无效的费率扣除类型")

    @stop_validate_if_error_occurred
    def validate_start_time(self, value):
        try:
            self.start_time.data = DateTimeKit.str_to_datetime(value.data, DateTimeFormatEnum.HOURS_MINUTES_FORMAT)
        except Exception as e:
            raise StopValidation("无效的时间格式")

    @stop_validate_if_error_occurred
    def validate_end_time(self, value):
        try:
            self.end_time.data = DateTimeKit.str_to_datetime(value.data, DateTimeFormatEnum.HOURS_MINUTES_FORMAT)
        except Exception as e:
            raise StopValidation("无效的时间格式")

    @stop_validate_if_error_occurred
    def validate_maintain_begin(self, value):
        try:
            if value.data:
                self.maintain_begin.data = DateTimeKit.str_to_datetime(value.data)
        except Exception as e:
            raise StopValidation("无效的时间格式")

    @stop_validate_if_error_occurred
    def validate_maintain_end(self, value):
        try:
            if value.data:
                self.maintain_end.data = DateTimeKit.str_to_datetime(value.data)
        except Exception as e:
            raise StopValidation("无效的时间格式")

    @stop_validate_if_error_occurred
    def validate_banks(self, value):
        try:
            [PaymentBankEnum(int(item)) for item in value.data]
        except Exception as e:
            raise StopValidation("无效的银行")


##########################################################################
# 引导规则 新增引导规则
##########################################################################

class ChannelRouterBaseForm(BaseForm):
    merchants = StringField(description="商户名称列表")
    uid_list = IntegerField(description="用户Id列表")
    interface = StringField(description="接入类型")
    amount_min = StringField(description="交易金额最小限制")
    amount_max = StringField(description="交易金额最大限制")

    @stop_validate_if_error_occurred
    def validate_amount_min(self, value):
        try:
            if value.data:
                self.amount_min.data = Decimal(str(value.data))
                BalanceKit.multiple_hundred(self.amount_min.data)
            else:
                self.amount_min.data = 0
        except Exception as e:
            raise StopValidation("无效的 amount_min")

    @stop_validate_if_error_occurred
    def validate_amount_max(self, value):
        try:
            if value.data:
                self.amount_max.data = Decimal(str(value.data))
                BalanceKit.multiple_hundred(self.amount_max.data)
            else:
                self.amount_max.data = 0
        except Exception as e:
            raise StopValidation("无效的 amount_max")

    @stop_validate_if_error_occurred
    def validate_merchants(self, value):
        try:
            if value.data:
                self.merchants.data = [MerchantEnum.from_name(x) for x in value.data]
            else:
                self.merchants.data = []
        except Exception as e:
            raise StopValidation("无效的 merchants 参数")

    @stop_validate_if_error_occurred
    def validate_interface(self, value):
        try:
            if value.data:
                self.interface.data = InterfaceTypeEnum.from_name(value.data)
            else:
                self.interface.data = None
        except Exception as e:
            raise StopValidation("无效的 interface")


class ChannelRouterAddForm(ChannelRouterBaseForm):
    """
    运营在新增商户时，配置商户的基本信息表单
    """
    config_list = StringField(description="规则")

    @stop_validate_if_error_occurred
    def validate_config_list(self, value):
        try:
            config_list = list()
            for x in value.data:
                x['payment_type'] = PaymentTypeEnum.from_name(x['payment_type'])
                x['priority'] = int(x['priority'])
                config_list.append(x)
            self.config_list.data = config_list
        except Exception as e:
            raise StopValidation("无效的 config_list")


class ChannelRouter2AddForm(ChannelRouterBaseForm):
    """
    运营在新增商户时，配置商户的基本信息表单
    """
    channel = StringField(description="渠道")

    @stop_validate_if_error_occurred
    def validate_channel(self, value):
        try:
            self.channel.data = ChannelConfigEnum(int(value.data))
        except Exception as e:
            raise StopValidation("无效的 channel")


##########################################################################
# 引导规则 更新引导规则
##########################################################################
class ChannelRouterUpdateForm(ChannelRouterAddForm):
    """
    运营在新增商户时，配置商户的基本信息表单
    """
    router_id = IntegerField(validators=[DataRequired()], description="规则Id")
