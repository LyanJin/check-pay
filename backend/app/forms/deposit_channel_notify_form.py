# -*-coding:utf8-*-
"""
表单验证
"""
from wtforms import StringField, IntegerField, FormField, Form
from wtforms.validators import DataRequired
from app.forms.base_form import BaseForm


class ThirdPayForm(BaseForm):
    """
    第三方支付 回调报文
    """
    code = IntegerField(validators=[DataRequired()], description="状态码")
    msg = StringField(description="状态描述")
    ts = IntegerField(validators=[DataRequired()], description="时间戳")
    sign = StringField(validators=[DataRequired()], description="参数签名")


class PonyPayForm(BaseForm):
    """
    Pony pay 回调报文
    """
    merchant_id = StringField(validators=[DataRequired()], description="商户号")
    porder = StringField(validators=[DataRequired()], description="平台订单号")
    orderid = StringField(validators=[DataRequired()], description="商户订单号")
    money = StringField(validators=[DataRequired()], description="订单金额")
    status = StringField(validators=[DataRequired()], description="交易状态")
    sign = StringField(validators=[DataRequired()], description="签名")


class PonyPayWithdrawForm(BaseForm):
    """
    Pony pay 提现回调报文
    参数名称	参数含义	参与签名	参数说明
    merchant_id	商户编号	是	 商户号
    corderid	订单号	是	 商户订单号
    money	订单金额	是	 订单金额
    status	交易状态	否	1 为已成功，2,为作废（金额退回）。
    sign	签名	否
    """
    merchant_id = StringField(validators=[DataRequired()], description="商户号")
    corderid = StringField(validators=[DataRequired()], description="平台订单号")
    money = StringField(validators=[DataRequired()], description="订单金额")
    status = StringField(validators=[DataRequired()], description="交易状态")
    sign = StringField(validators=[DataRequired()], description="签名")


class ProductForm(Form):
    """
    提现计费表单
    """
    subject = StringField(
        validators=[DataRequired()],
        description="商品名称"
    )

    body = IntegerField(
        # validators=[DataRequired()],
        description="商品描述",
        default="",
    )


class ZhuanYeFuWithdrawForm(BaseForm):
    """
    ZYF pay 提现回调报文
    参数名称	       参数含义	  必填     类型	参数说明
    type	       支付类型	   是	 string  1: 网银支付， 2： 支付宝， 3：微信
    channel	       渠道类型	   是	 string  1: 银行编码（传0 则跳转至银行选择页面）， 2：银行编码， 3，4，5，6 （1(小额) , 2(扫码),3( APP)）
    order	       商户订单号    是	 string
    transaction	   平台订单号    是	 string  1 为已成功，2,为作废（金额退回）。
    current	       币种         是    int
    amount         金额         是    decimal
    fee            汇率         是    decimal
    refund_amount  退款金额      否    decimal
    refund_fee     退款手续费    否     decimal
    time           订单生成时间   是    timeatmp
    time_close     订单有效时间   是    timeatmp
    time_finish    订单成功时间   否    timeatmp
    subject        商品名称      是     string
    body           商品描述      否     string
    status         状态         是      int
    remark         订单备注      否      string
    """
    type = StringField(validators=[DataRequired()], description="支付类型")
    channel = StringField(default=0, description="渠道类型")
    order = StringField(validators=[DataRequired()], description="商户订单号")
    transaction = StringField(validators=[DataRequired()], description="平台订单号")
    currency = StringField(validators=[DataRequired()], description="币种")
    amount = StringField(validators=[DataRequired()], description="金额")
    fee = StringField(validators=[DataRequired()], description="费率")
    refund_amount = StringField(description="退款金额")
    refund_fee = StringField(description="退款手续费")
    time = StringField(validators=[DataRequired()], description="订单生成时间")
    time_close = StringField(validators=[DataRequired()], description="订单有效时间")
    time_finish = StringField(description="订单成功时间")
    product = FormField(ProductForm)
    status = StringField(validators=[DataRequired()], description="状态")
    remark = StringField(description="订单备注")


class JifuCallbackForm(BaseForm):
    """
    极付回调表单
    """
    sign = StringField(description="签名")
    nonce_str = StringField(description="六位随机字符")
    id = StringField(description="订单唯一code id")
    money = StringField(description="交易金额")
    remark = StringField(description="系统订单号")

    sign_fields = ['nonce_str', 'id', 'money', 'remark']

    def get_sign_fields(self):
        """
        参与签名的字段
        :return:
        """
        return dict([(k, v) for k, v in self.form_data.items() if k in self.sign_fields and v])

    def get_raw_sign(self):
        """
        传入的签名
        :return:
        """
        return self.form_data['sign']


class KhpayForm(BaseForm):
    """
    快汇支付 回调报文
    """
    custid = StringField(validators=[DataRequired()], description="商户号")
    ordid = StringField(validators=[DataRequired()], description="广汇通 入款编号")
    client_ordid = StringField(validators=[DataRequired()], description="商户自定义入款编号")
    companyname = StringField(validators=[DataRequired()], description="商户公司名")
    channel = StringField(validators=[DataRequired()], description="支付渠道 ['bank','wechat','alipay']")
    bankcode = StringField(validators=[DataRequired()], description="付款方银行代码")
    bgreturl = StringField(validators=[DataRequired()], description="订单回调纲址")
    accountid = StringField(validators=[DataRequired()], description="付款人卡号")
    accountname = StringField(validators=[DataRequired()], description="付款人姓名")
    amount = StringField(validators=[DataRequired()], description="附言")
    remark = StringField(validators=[], description="商户公司名")
    status = StringField(validators=[DataRequired()], description="订单状态 [finish,fail]")
    message = StringField(validators=[DataRequired()], description="订单信息")
    trans_at = StringField(validators=[DataRequired()], description="交易日期")
    created_at = StringField(validators=[DataRequired()], description="订单创建时间")
    updated_at = StringField(validators=[DataRequired()], description="订单更新時間")
    sig = StringField(validators=[DataRequired()], description="签名")

class YinSaoForm(BaseForm):
    """
    快汇支付 回调报文
    """
    version = StringField(description="版本号")
    merNo = StringField(description="平台提供的商户编号")
    orderNo = StringField(description="商户订单编号")
    orderDate = StringField(description="订单日期")
    transId = StringField(description="交易类型")
    transAmt = StringField(description="支付金额")
    respCode = StringField(description="交易返回码,返回0000表示交易成功")
    respDesc = StringField(description="消息说明")
    signature = StringField(description="签名")
