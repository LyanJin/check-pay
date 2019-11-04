"""
"""
from flask import current_app
from wtforms import StringField
from wtforms.validators import DataRequired, length, Regexp, StopValidation
from wtforms import ValidationError

from app.constants import auth_code as mobile_constants
from app.forms.base_form import stop_validate_if_error_occurred, BaseForm
from app.forms.domain_form import DomainForm
from app.libs.balance_kit import BalanceKit
from app.libs.error_code import AccountNotExistError, AccountAlreadyExitError
from app.libs.string_kit import PhoneNumberParser
from app.logics.mobile.auth_code import AuthCodeGenerator
from app.models.user import User
from decimal import Decimal
from app.libs.custom_form import StringRequired, DecimalRequired


class MobileNumberForm(DomainForm):
    number = StringField(
        validators=[
            DataRequired(message="手机号不能为空！"),
            length(min=mobile_constants.NUMBER_MIN_LENGTH,
                   message="手机号码长度必须大于等于%s位数" % mobile_constants.NUMBER_MIN_LENGTH),
            length(max=mobile_constants.NUMBER_MAX_LENGTH,
                   message="手机号码长度必须小于等于%s位数" % mobile_constants.NUMBER_MAX_LENGTH),
        ],
        description="手机区号+号码"
    )

    @stop_validate_if_error_occurred
    def validate_number(self, number):
        """
        验证手机号码
        :param number:
        :return:
        """
        # 去掉中间的空格和两边的空格
        data = ''.join(number.data.split(' ')).strip()

        if not data.startswith('+'):
            raise ValidationError("区号必须以+号开头")

        if not data.strip('+').isdigit():
            raise ValidationError("号码必须全是数字")

        if not PhoneNumberParser.is_valid_number(data):
            raise ValidationError("你输入了无效的手机号，请重新输入")

        self.number.data = data


class MobileRegisterCheckForm(MobileNumberForm):

    @classmethod
    def request_validate(cls):
        """
        数据库中检查手机号码是否已经注册
        :return:
        """
        form, error = super(MobileRegisterCheckForm, cls).request_validate()

        if not error:
            if User.query_user(form.merchant.data, account=form.number.data):
                error = AccountAlreadyExitError()

        return form, error


class MobileRegisterTrueCheckForm(MobileNumberForm):

    @classmethod
    def request_validate(cls):
        """
        数据库中检查手机号码是否已经注册
        :return:
        """
        form, error = super(MobileRegisterTrueCheckForm,
                            cls).request_validate()

        if not error:
            if not User.query_user(form.merchant.data, account=form.number.data):
                error = AccountNotExistError()

        return form, error


class AuthCodeTrueForm(MobileRegisterTrueCheckForm):
    auth_code = StringField(
        validators=[
            DataRequired(),
            length(
                min=mobile_constants.AUTH_CODE_LENGTH,
                max=mobile_constants.AUTH_CODE_LENGTH,
                message="验证码必须是%s位数" % mobile_constants.AUTH_CODE_LENGTH,
            ),
        ],
        description="短信动态验证码"
    )

    @stop_validate_if_error_occurred
    def validate_auth_code(self, auth_code):
        """
        验证短信验证码
        :param auth_code:
        :return:
        """
        # 验证码格式判断
        if not auth_code.data.isdigit():
            raise ValidationError('验证码必须全为数字')


class AuthCodeForm(MobileRegisterCheckForm):
    auth_code = StringField(
        validators=[
            DataRequired(),
            length(
                min=mobile_constants.AUTH_CODE_LENGTH,
                max=mobile_constants.AUTH_CODE_LENGTH,
                message="验证码必须是%s位数" % mobile_constants.AUTH_CODE_LENGTH,
            ),
        ],
        description="短信动态验证码"
    )

    @stop_validate_if_error_occurred
    def validate_auth_code(self, auth_code):
        """
        验证短信验证码
        :param auth_code:
        :return:
        """
        # 验证码格式判断
        if not auth_code.data.isdigit():
            raise ValidationError('验证码必须全为数字')

        # if not AuthCodeGenerator(self.number.data).verify_code(auth_code.data):
        #     raise AuthFailed("验证码错误")


class PasswordForm(AuthCodeForm):
    password = StringField(
        validators=[
            DataRequired(message="密码不能为空"),
            length(min=mobile_constants.PASSWORD_MIN_LENGTH,
                   message="密码长度必须大于等于%s位数" % mobile_constants.PASSWORD_MIN_LENGTH),
            length(max=mobile_constants.PASSWORD_MAX_LENGTH,
                   message="密码长度必须小于等于%s位数" % mobile_constants.PASSWORD_MAX_LENGTH),
        ],
        description="密码"
    )


class PasswordTrueForm(AuthCodeTrueForm):
    password = StringField(
        validators=[
            DataRequired(message="密码不能为空"),
            length(min=mobile_constants.PASSWORD_MIN_LENGTH,
                   message="密码长度必须大于等于%s位数" % mobile_constants.PASSWORD_MIN_LENGTH),
            length(max=mobile_constants.PASSWORD_MAX_LENGTH,
                   message="密码长度必须小于等于%s位数" % mobile_constants.PASSWORD_MAX_LENGTH),
        ],
        description="密码"
    )


class ResetWordVerify(DomainForm):
    ori_password = StringField(
        validators=[
            DataRequired(message="原始密码不能为空"),
            length(min=mobile_constants.PASSWORD_MIN_LENGTH,
                   message="密码长度必须大于等于%s位数" % mobile_constants.PASSWORD_MIN_LENGTH),
            length(max=mobile_constants.PASSWORD_MAX_LENGTH,
                   message="密码长度必须小于等于%s位数" % mobile_constants.PASSWORD_MAX_LENGTH),
        ],
        description="原始密码"
    )


class ResetWordForm(ResetWordVerify):
    new_password = StringField(
        validators=[
            DataRequired(message="新密码不能为空"),
            length(min=mobile_constants.PASSWORD_MIN_LENGTH,
                   message="密码长度必须大于等于%s位数" % mobile_constants.PASSWORD_MIN_LENGTH),
            length(max=mobile_constants.PASSWORD_MAX_LENGTH,
                   message="密码长度必须小于等于%s位数" % mobile_constants.PASSWORD_MAX_LENGTH),
        ],
        description="重置密码"
    )


class SetPaymentPassword(DomainForm):
    payment_password = StringField(
        validators=[
            DataRequired(message="支付密码不能为空"),
            length(
                min=mobile_constants.PAYMENT_PASSWORD_MD5_LENGTH,
                max=mobile_constants.PAYMENT_PASSWORD_MD5_LENGTH,
                message="支付密码必须是%s位数" % mobile_constants.PAYMENT_PASSWORD_MD5_LENGTH,
            ),
        ],
        description="支付密码"
    )


class OldPaymentPassword(DomainForm):
    ori_payment_password = StringField(
        validators=[
            DataRequired(message="支付密码不能为空"),
            length(
                min=mobile_constants.PAYMENT_PASSWORD_MD5_LENGTH,
                max=mobile_constants.PAYMENT_PASSWORD_MD5_LENGTH,
                message="支付密码必须是%s位数" % mobile_constants.PAYMENT_PASSWORD_MD5_LENGTH,
            ),
        ],
        description="原始支付密码"
    )


class ResetPaymentPasswordForm(OldPaymentPassword):
    new_payment_password = StringField(
        validators=[
            DataRequired(message="支付密码不能为空"),
            length(
                min=mobile_constants.PAYMENT_PASSWORD_MD5_LENGTH,
                max=mobile_constants.PAYMENT_PASSWORD_MD5_LENGTH,
                message="支付密码必须是%s位数" % mobile_constants.PAYMENT_PASSWORD_MD5_LENGTH,
            ),
        ],
        description="新支付密码"
    )


class SetForgetPaymentPasswordForm(AuthCodeTrueForm):
    new_payment_password = StringField(
        validators=[
            DataRequired(message="支付密码不能为空"),
            length(
                min=mobile_constants.PAYMENT_PASSWORD_MD5_LENGTH,
                max=mobile_constants.PAYMENT_PASSWORD_MD5_LENGTH,
                message="支付密码必须是%s位数" % mobile_constants.PAYMENT_PASSWORD_MD5_LENGTH,
            ),
        ],
        description="新支付密码"
    )


class BankCardForm(DomainForm):
    card_id = StringField(
        validators=[
            DataRequired(message="银行卡卡号不能为空"),
        ],
        description="银行卡卡号"
    )


class CreateBankCardForm(SetPaymentPassword):
    """
    添加银行卡的表单验证
    """
    bank_name = StringField(validators=[DataRequired()], description="银行名称")
    bank_code = StringField(validators=[DataRequired()], description="银行编码")
    card_no = StringField(validators=[DataRequired()], description="银行卡卡号")
    account_name = StringField(validators=[DataRequired()], description="开户人")
    branch = StringField(validators=[], description="支行")
    province = StringField(validators=[DataRequired()], description="省份")
    city = StringField(validators=[DataRequired()], description="城市")


class DeleteBankCardForm(SetPaymentPassword):
    """
    添加银行卡的表单验证
    """
    bank_card_id = StringField(
        validators=[DataRequired()], description="银行卡id")


class TransferForm(DomainForm):
    """
    转账表单验证
    """
    number = StringField(validators=[DataRequired()], description="手机号码")
    zone = StringField(validators=[], description="区号")
    amount = StringField(validators=[DataRequired(
    ), DecimalRequired()], description="转账金额最小0.01 最大45000")
    comment = StringField(
        validators=[length(max=10, message="备注不能超过%s个字符" % 10)], description="转账说明")
    payment_password = StringField(
        validators=[
            DataRequired(message="支付密码不能为空"),
            length(
                min=mobile_constants.PAYMENT_PASSWORD_MD5_LENGTH,
                max=mobile_constants.PAYMENT_PASSWORD_MD5_LENGTH,
                message="支付密码必须是%s位数" % mobile_constants.PAYMENT_PASSWORD_MD5_LENGTH,
            ),
        ],
        description="支付密码"
    )

    @stop_validate_if_error_occurred
    def validate_amount(self, value):
        try:
            self.amount.data = Decimal(value.data)
            BalanceKit.multiple_hundred(self.amount.data)
        except Exception as e:
            raise StopValidation("无效的 amount，必须是整数或浮点数字符串，最多保留2位小数")

    def join_phone_number(self):
        account = ''.join([d for d in [self.zone.data, self.number.data] if d])
        account = '+' + account.strip('+').strip()
        if not PhoneNumberParser.is_valid_number(account):
            return None
        return account


class TransferAccountQueryForm(DomainForm):
    """
    转账账号查询
    """
    zone = StringField(validators=[], description="区号")
    account = StringField(validators=[DataRequired()], description="账号")

    def join_phone_number(self):
        account = ''.join([d for d in [self.zone.data, self.account.data] if d])
        account = '+' + account.strip('+').strip()
        if not PhoneNumberParser.is_valid_number(account):
            return None
        return account
