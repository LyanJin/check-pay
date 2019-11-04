"""
表单验证
"""
from wtforms import StringField, IntegerField
from wtforms.validators import DataRequired, length, Regexp
from wtforms import ValidationError

from app.enums.account import AccountTypeEnum, AuthTypeEnum
from app.models.user import User
from app.forms.base_form import BaseForm, stop_validate_if_error_occurred
from app.forms.auth_code import MobileNumberForm


class LoginForm(MobileNumberForm):
    password = StringField(validators=[
        DataRequired(message='密码不能为空'),
        # length(min=mobile_constants.PASSWORD_MIN_LENGTH,
        #        message="手机号码长度必须大于等于%s位数" % mobile_constants.PASSWORD_MIN_LENGTH),
        # length(max=mobile_constants.PASSWORD_MAX_LENGTH,
        #        message="手机号码长度必须小于等于%s位数" % mobile_constants.PASSWORD_MAX_LENGTH),
        # Regexp(r'(?![0-9]+$)(?![a-zA-Z]+$)[0-9A-Za-z_&-]{6,16}$', message="密码格式有误")
        ],
        description='密码'
    )


class ClientForm(BaseForm):
    account = StringField(validators=[DataRequired(), length(min=5, max=32)])
    ac_type = IntegerField(validators=[DataRequired()])
    auth_type = IntegerField(validators=[DataRequired()])
    password = StringField()

    @stop_validate_if_error_occurred
    def validate_ac_type(self, value):
        try:
            _type = AccountTypeEnum(value.data)
        except ValueError as e:
            raise e
        self.ac_type.data = _type

    @stop_validate_if_error_occurred
    def validate_auth_type(self, value):
        try:
            _type = AuthTypeEnum(value.data)
        except ValueError as e:
            raise e
        self.auth_type.data = _type


class UserMobileForm(ClientForm):
    account = StringField(validators=[
        Regexp(r'^[0-9]{6,22}$')
    ])
    password = StringField(validators=[
        DataRequired(),
        # password can only include letters , numbers and "_"
        Regexp(r'^[A-Za-z0-9]{6,22}$')
    ])

    @stop_validate_if_error_occurred
    def validate_account(self, value):
        if User.query.filter_by(account=value.data).first():
            raise ValidationError("账号已经存在")
