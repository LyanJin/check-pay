from decimal import Decimal

from wtforms import StringField, IntegerField
from wtforms.validators import DataRequired, StopValidation

from app.enums.balance import ManualAdjustmentType
from app.forms.base_form import stop_validate_if_error_occurred
from app.forms.base_form import BaseForm
from app.models.merchant import MerchantInfo
from config import MerchantEnum


class MerchantBalanceEditForm(BaseForm):
    name = StringField(
        validators=[
            DataRequired(),
        ],
        description='商户名称'
    )
    adjustment_type = StringField(
        validators=[
            DataRequired(),
        ],
        description='调整类型'
    )
    amount = StringField(
        validators=[
            DataRequired(),
        ],
        description='金额'
    )
    reason = StringField(
        validators=[
            DataRequired(),
        ],
        description='原因'
    )

    # 由adjustment_type生成的
    bl_type = IntegerField()
    ad_type = IntegerField()

    @stop_validate_if_error_occurred
    def validate_name(self, value):
        try:
            self.name.data = MerchantEnum.from_name(value.data)
        except Exception:
            raise StopValidation("无效的商户名称")

        if not MerchantInfo.query_merchant(self.name.data):
            raise StopValidation("未创建的商户")

    @stop_validate_if_error_occurred
    def validate_adjustment_type(self, value):
        try:
            self.bl_type.data, self.ad_type.data = ManualAdjustmentType(value.data).get_balance_adjustment_type()
        except Exception:
            raise StopValidation("无效的调整类型")

    @stop_validate_if_error_occurred
    def validate_amount(self, value):
        try:
            self.amount.data = Decimal(value.data)
        except Exception:
            raise StopValidation("无效的金额")
