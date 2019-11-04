from wtforms import StringField
from wtforms.validators import StopValidation, DataRequired

from app.enums.trade import PayTypeEnum
from app.forms.base_form import BaseForm, stop_validate_if_error_occurred
from config import MerchantEnum


class DepositConfigForm(BaseForm):
    """
    充值配置获取
    """
    sign = StringField(validators=[DataRequired(message="sign是必填字段")], description="签名")
    merchant_id = StringField(validators=[DataRequired(message="merchant_id是必填字段")], description="商户ID")
    user_ip = StringField(validators=[DataRequired(message="user_ip是必填的")], description="用户IP")
    user_id = StringField(validators=[], description="用户ID")

    sign_fields = ['merchant_id', 'user_ip']

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
    def validate_payment_way(self, value):
        try:
            self.payment_way.data = PayTypeEnum.from_name(value.data)
        except Exception as e:
            raise StopValidation("无效的 payment_way")
