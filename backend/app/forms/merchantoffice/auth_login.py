from wtforms.validators import DataRequired, length, StopValidation
from app.constants import auth_code as user_constants
from app.enums.trade import OrderStateEnum, PayTypeEnum
from app.forms.base_form import BaseForm, stop_validate_if_error_occurred
from wtforms import StringField, IntegerField

from app.libs.datetime_kit import DateTimeKit, DateTimeFormatEnum
from app.libs.order_kit import OrderUtils
from config import MerchantEnum


class MerchantLoginForm(BaseForm):
    """
        back office 登陆 表单
    """
    account = StringField(
        validators=[
            DataRequired(message='账户名不能为空')
        ],
        description='商户名'
    )
    password = StringField(
        validators=[
            DataRequired(message='密码不能为空'),
            length(min=user_constants.PASSWORD_MIN_LENGTH, max=user_constants.PASSWORD_MAX_LENGTH,
                   message="密码长度必须等于%s位数" % user_constants.PASSWORD_MIN_LENGTH),
        ],
        description='密码'
    )

    @stop_validate_if_error_occurred
    def validate_account(self, value):
        try:
            self.account.data = MerchantEnum.from_name(value.data)
        except Exception as e:
            raise StopValidation("无效的商户名称")


class DepositOrderSelectForm(BaseForm):
    order_id = StringField(default='', description='商户订单号/系统订单号')
    start_datetime = StringField(default='', description='订单开始时间')
    end_datetime = StringField(default='', description='订单结束时间')
    state = StringField(default='0', description='订单状态')
    page_size = IntegerField(validators=[DataRequired()], description="单页数据条数")
    page_index = IntegerField(validators=[DataRequired()], description="页码")

    @stop_validate_if_error_occurred
    def validate_start_datetime(self, value):
        if value.data == '':
            self.start_datetime.data = DateTimeKit.get_day_begin_end(DateTimeKit.get_cur_date())[0]
        else:
            try:
                self.start_datetime.data = DateTimeKit.str_to_datetime(value.data, DateTimeFormatEnum.SECONDS_FORMAT)
            except Exception as e:
                raise StopValidation('查询日期格式有误')

    @stop_validate_if_error_occurred
    def validate_end_datetime(self, value):
        if value.data == '':
            self.end_datetime.data = DateTimeKit.get_day_begin_end(DateTimeKit.get_cur_date())[1]
        else:
            try:
                self.end_datetime.data = DateTimeKit.str_to_datetime(value.data, DateTimeFormatEnum.SECONDS_FORMAT)
            except Exception as e:
                raise StopValidation('查询日期格式有误')

    @stop_validate_if_error_occurred
    def validate_state(self, value):
        try:
            if value.data == "0":
                self.state.data = "0"
            else:
                state = int(value.data) if int(value.data) in [10, 30, 40] else 0
                self.state.data = OrderStateEnum(state)
        except Exception as e:
            raise StopValidation("无效的订单状态")

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


class WithdrawOrderSelectForm(BaseForm):
    order_id = StringField(default='', description='商户订单号/系统订单号')
    start_datetime = StringField(default='', description='订单开始时间')
    end_datetime = StringField(default='', description='订单结束时间')
    state = StringField(default='0', description='订单状态')
    page_size = IntegerField(validators=[DataRequired()], description="单页数据条数")
    page_index = IntegerField(validators=[DataRequired()], description="页码")

    @stop_validate_if_error_occurred
    def validate_start_datetime(self, value):
        if value.data == '':
            self.start_datetime.data = DateTimeKit.get_day_begin_end(DateTimeKit.get_cur_date())[0]
        else:
            try:
                self.start_datetime.data = DateTimeKit.str_to_datetime(value.data, DateTimeFormatEnum.SECONDS_FORMAT)
            except Exception as e:
                raise StopValidation('查询日期格式有误')

    @stop_validate_if_error_occurred
    def validate_end_datetime(self, value):
        if value.data == '':
            self.end_datetime.data = DateTimeKit.get_day_begin_end(DateTimeKit.get_cur_date())[1]
        else:
            try:
                self.end_datetime.data = DateTimeKit.str_to_datetime(value.data, DateTimeFormatEnum.SECONDS_FORMAT)
            except Exception as e:
                raise StopValidation('查询日期格式有误')

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


#########################################################################
# 订单通知
#########################################################################

class OrderStateNotifyFrom(BaseForm):
    """
    订单通知
    """
    order_id = StringField(validators=[DataRequired(), length(min=OrderUtils.PREFIX_LENGTH)], description="订单Id")
    type = StringField(validators=[DataRequired()], description="类型")

    @stop_validate_if_error_occurred
    def validate_type(self, value):
        try:
            self.type.data = PayTypeEnum(int(value.data))
        except Exception as e:
            raise StopValidation("无效的订单类型")

    @stop_validate_if_error_occurred
    def validate_order_id(self, value):
        try:
            self.order_id.data = value.data
        except Exception as e:
            raise StopValidation("无效的 order_id")

