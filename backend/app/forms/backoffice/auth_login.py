from wtforms import StringField
from wtforms.validators import DataRequired, length
from app.constants import auth_code as user_constants
from app.forms.base_form import BaseForm


class AdminTestRegisterForm(BaseForm):
    """
        back office 登陆 表单
    """
    account = StringField(
        validators=[
            DataRequired(message='账户名不能为空'),
            length(max=user_constants.BACKOFFICE_USERNAME_MAX_LENGTH,
                   message='用户名最大不能多于%s位' % user_constants.BACKOFFICE_USERNAME_MAX_LENGTH)
        ],
        description='用户名'
    )
    password = StringField(
        validators=[
            DataRequired(message='密码不能为空'),
        ],
        description='密码'
    )


class AuthLoginForm(BaseForm):
    """
        back office 登陆 表单
    """
    account = StringField(
        validators=[
            DataRequired(message='账户名不能为空'),
            length(max=user_constants.BACKOFFICE_USERNAME_MAX_LENGTH,
                   message='用户名最大不能多于%s位' % user_constants.BACKOFFICE_USERNAME_MAX_LENGTH)
        ],
        description='用户名'
    )
    password = StringField(
        validators=[
            DataRequired(message='密码不能为空'),
            length(min=user_constants.PASSWORD_MIN_LENGTH, max=user_constants.PASSWORD_MAX_LENGTH,
                   message="密码长度必须等于%s位数" % user_constants.PASSWORD_MIN_LENGTH),
        ],
        description='密码'
    )


class ResetWordVerify(BaseForm):
    ori_password = StringField(
        validators=[
            DataRequired(message="原始密码不能为空"),
            length(min=user_constants.PASSWORD_MIN_LENGTH,
                   message="密码长度必须大于等于%s位数" % user_constants.PASSWORD_MIN_LENGTH),
            length(max=user_constants.PASSWORD_MAX_LENGTH,
                   message="密码长度必须小于等于%s位数" % user_constants.PASSWORD_MAX_LENGTH),
        ],
        description="原始密码"
    )


class ResetWordForm(ResetWordVerify):
    new_password = StringField(
        validators=[
            DataRequired(message="新密码不能为空"),
            length(min=user_constants.PASSWORD_MIN_LENGTH,
                   message="密码长度必须大于等于%s位数" % user_constants.PASSWORD_MIN_LENGTH),
            length(max=user_constants.PASSWORD_MAX_LENGTH,
                   message="密码长度必须小于等于%s位数" % user_constants.PASSWORD_MAX_LENGTH),
        ],
        description="重置密码"
    )
