from wtforms import StringField, IntegerField
from wtforms.validators import DataRequired, length, StopValidation
from app.constants import auth_code as mobile_constants
from app.enums.trade import BalanceAdjustTypeEnum, PayTypeEnum

from app.forms.base_form import BaseForm, stop_validate_if_error_occurred

#########################
# 用户数据查询
#########################
from app.libs.datetime_kit import DateTimeKit, DateTimeFormatEnum


class UserListSelectForm(BaseForm):
    """
    用户数据查询
    """

    phone_number = StringField(default='', description="手机号")
    start_datetime = StringField(default='', description='查询开始时间')
    end_datetime = StringField(default='', description='查询结束时间')
    page_size = IntegerField(validators=[DataRequired()], description="单页数据条数")
    page_index = IntegerField(validators=[DataRequired()], description="页码")

    @stop_validate_if_error_occurred
    def validate_start_datetime(self, value):
        if not value.data:
            self.start_datetime.data = None
        else:
            try:
                self.start_datetime.data = DateTimeKit.str_to_datetime(value.data, DateTimeFormatEnum.SECONDS_FORMAT)
            except Exception as e:
                raise StopValidation('查询日期格式有误')

    @stop_validate_if_error_occurred
    def validate_end_datetime(self, value):
        if not value.data:
            self.end_datetime.data = None
        else:
            try:
                self.end_datetime.data = DateTimeKit.str_to_datetime(value.data, DateTimeFormatEnum.SECONDS_FORMAT)
            except Exception as e:
                raise StopValidation('查询日期格式有误')

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


#####################
# 钱包端用户详情展示
#####################

class UserInfoForm(BaseForm):
    """
    用户数据查询
    """

    uid = StringField(validators=[DataRequired()], description="用户id")


###############################
# 用户余额调整
###############################

class UserBalanceEditForm(BaseForm):
    uid = StringField(validators=[DataRequired()], description="用户id")
    adjust_type = StringField(validators=[DataRequired()], description="余额调整类型")
    amount = StringField(validators=[DataRequired()], description="调整金额")
    comment = StringField(validators=[DataRequired()], description="备注")

    @stop_validate_if_error_occurred
    def validate_adjust_type(self, value):
        try:
            self.adjust_type.data = BalanceAdjustTypeEnum(int(value.data))
        except Exception as e:
            raise StopValidation("无效的余额调整类型")


#####################
# 用户最近一周交易记录
#####################

class UserTransactionForm(BaseForm):
    """
    用户数据查询
    """

    uid = StringField(validators=[DataRequired()], description="用户id")
    pay_type = StringField(validators=[DataRequired()], description="交易类型： 充值/提现")
    page_size = IntegerField(validators=[DataRequired()], description="单页数据条数")
    page_index = IntegerField(validators=[DataRequired()], description="页码")

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
    def validate_pay_type(self, value):
        try:

            if value.data not in ["1", "2"]:
                raise StopValidation("无效的交易类型")

            self.pay_type.data = PayTypeEnum(int(value.data))
        except Exception as e:
            raise StopValidation("无效的交易类型")


###############################
# 编辑用户银行卡信息
###############################

class UserBankDeleteForm(BaseForm):
    card_id = StringField(validators=[DataRequired()], description="银行卡Id")
