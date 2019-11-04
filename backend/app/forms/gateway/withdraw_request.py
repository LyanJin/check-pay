from decimal import Decimal

from wtforms import StringField, IntegerField, DecimalField
from wtforms.validators import StopValidation, DataRequired

from app.enums.trade import PaymentTypeEnum, PaymentBankEnum
from app.forms.base_form import BaseForm, stop_validate_if_error_occurred
from app.libs.balance_kit import BalanceKit
from config import MerchantEnum


class WithdrawRequestForm(BaseForm):
    """
    充值API的表单
    """
    sign = StringField(validators=[DataRequired(message="sign是必填字段")], description="签名")
    merchant_id = StringField(validators=[DataRequired(message="merchant_id是必填字段")], description="商户ID")
    amount = StringField(validators=[DataRequired(message="amount是必填字段")], description="充值金额")
    mch_tx_id = StringField(validators=[DataRequired(message="mch_tx_id是必填字段")], description="商户订单号")
    notify_url = StringField(validators=[DataRequired(message="notify_url是必填字段")], description="回调通知URL")
    bank_type = StringField(validators=[DataRequired(message="bank_type是必填字段")], description="银行类型")
    card_no = StringField(validators=[DataRequired(message="card_no是必填字段")], description="收款卡号")
    account_name = StringField(validators=[DataRequired(message="account_name是必填字段")], description="收款人姓名")
    province = StringField(validators=[DataRequired(message="province是必填字段")], description="省份名称")
    city = StringField(validators=[DataRequired(message="city是必填字段")], description="城市名称")
    branch = StringField(validators=[], description="支行名称")
    user_id = StringField(validators=[], description="用户ID")
    user_ip = StringField(validators=[DataRequired(message="user_ip是必填字段")], description="发起请求的用户ip")
    extra = StringField(validators=[], description="透传数据")

    sign_fields = ['merchant_id', 'amount', 'mch_tx_id', 'notify_url', 'bank_type', 'card_no', 'account_name',
                   'province', 'city', 'user_ip']

    def get_sign_fields(self):
        """
        参与签名的字段
        :return:
        """
        return dict([(k, v) for k, v in self.json_data.items() if k in self.sign_fields])

    @stop_validate_if_error_occurred
    def validate_merchant_id(self, value):
        try:
            self.merchant_id.data = MerchantEnum(int(value.data))
        except Exception as e:
            raise StopValidation("无效的 merchant_id")

    @stop_validate_if_error_occurred
    def validate_bank_type(self, value):
        try:
            self.bank_type.data = PaymentBankEnum.from_name(value.data)
        except Exception as e:
            raise StopValidation("无效的 bank_type, 可用银行类型包括：%s" % PaymentBankEnum.get_desc_name_pairs())

    @stop_validate_if_error_occurred
    def validate_amount(self, value):
        try:
            self.amount.data = Decimal(value.data)
            BalanceKit.multiple_hundred(self.amount.data)
        except Exception as e:
            raise StopValidation("无效的 amount，必须是整数或浮点数字符串，最多保留2位小数")


class WithdrawNotifyForm(BaseForm):
    """
    充值回调通知
    """
    sign = StringField(validators=[DataRequired()], description="签名")
    merchant_id = IntegerField(validators=[DataRequired()], description="商户ID")
    amount = DecimalField(validators=[DataRequired()], description="发起金额")
    tx_amount = DecimalField(validators=[DataRequired()], description="实际支付金额")
    mch_tx_id = StringField(validators=[DataRequired()], description="商户订单号")
    sys_tx_id = StringField(validators=[DataRequired()], description="平台订单号")
    state = StringField(validators=[DataRequired()], description="订单状态")
    extra = StringField(validators=[], description="透传数据")

    sign_fields = ['merchant_id', 'amount', 'mch_tx_id', 'tx_amount', 'sys_tx_id', 'state']

    def get_sign_fields(self):
        """
        参与签名的字段
        :return:
        """
        return dict([(k, v) for k, v in self.json_data.items() if k in self.sign_fields])

    @stop_validate_if_error_occurred
    def validate_merchant_id(self, value):
        try:
            self.merchant_id.data = MerchantEnum(int(value.data))
        except Exception as e:
            raise StopValidation("无效的 merchant_id")

    @stop_validate_if_error_occurred
    def validate_amount(self, value):
        try:
            self.amount.data = Decimal(value.data)
            BalanceKit.multiple_hundred(self.amount.data)
        except Exception as e:
            raise StopValidation("无效的 amount，必须是整数或浮点数字符串，最多保留2位小数")

    @stop_validate_if_error_occurred
    def validate_tx_amount(self, value):
        try:
            self.tx_amount.data = Decimal(value.data)
            BalanceKit.multiple_hundred(self.tx_amount.data)
        except Exception as e:
            raise StopValidation("无效的 tx_amount，必须是整数或浮点数字符串，最多保留2位小数")
