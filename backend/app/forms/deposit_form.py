# -*-coding:utf8-*-
"""
表单验证
"""
from decimal import Decimal

from wtforms import StringField, IntegerField
from wtforms.validators import DataRequired, StopValidation
from app.enums.channel import ChannelConfigEnum
from app.enums.trade import PaymentTypeEnum, PayTypeEnum
from app.forms.domain_form import DomainForm
from app.libs.balance_kit import BalanceKit
from app.libs.custom_form import StringRequired
from app.forms.base_form import stop_validate_if_error_occurred


class AmountInputForm(DomainForm):
    """
    充值金额的输入
    """
    amount = StringField(validators=[DataRequired(message="amount是必填字段")], description="金额")

    @stop_validate_if_error_occurred
    def validate_amount(self, value):
        try:
            self.amount.data = Decimal(value.data)
            BalanceKit.multiple_hundred(self.amount.data)
        except Exception as e:
            raise StopValidation("无效的 amount，必须是整数或浮点数字符串，最多保留2位小数")


class CreateOrderForm(AmountInputForm):
    """
    用户充值： 充值金额及支付方式 payment_type
    """
    payment_type = StringField(validators=[DataRequired(), StringRequired()], description="支付类型")
    channel_id = StringField(validators=[DataRequired()], description="通道Id")

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


class CreateWithdrawOrderForm(AmountInputForm):
    """
    用户提现： 提现金额，到款银行卡，交易密码
    """
    user_bank = StringField(validators=[DataRequired()], description="用户银行卡编号")
    trade_password = StringField(validators=[DataRequired()], description="支付密码")


class UserOrderSelectForm(DomainForm):
    """
        用户订单查询：
    """
    year = IntegerField(validators=[DataRequired()], description="年")
    mouth = IntegerField(validators=[DataRequired()], description="月")
    page_index = IntegerField(default=1, description="页码")
    payment_type = IntegerField(description=PayTypeEnum.description())

    @stop_validate_if_error_occurred
    def validate_page_index(self, value):
        try:
            self.page_index.data = int(value.data)
        except:
            raise StopValidation("无效的page_index")

    @stop_validate_if_error_occurred
    def validate_payment_type(self, value):
        try:
            if not value.data or value.data == "0":
                self.payment_type.data = None
            else:
                self.payment_type.data = PayTypeEnum(int(value.data))
        except Exception as e:
            raise StopValidation("无效的payment_type")


class BestPayNotifyForm(DomainForm):
    """
        快手付转账记录：
    """
    tx_id = StringField(validators=[DataRequired()], description="流水号")
    amount = StringField(validators=[DataRequired()], description="存款金额")
    card_number = StringField(validators=[DataRequired()], description="存款卡号")
    bank_name = StringField(validators=[DataRequired()], description="存款银行")
    user_name = StringField(validators=[DataRequired()], description="用户名称")

