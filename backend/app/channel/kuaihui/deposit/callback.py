from flask import current_app

from app.channel.deposit_base import DepositCallbackBase
from app.enums.third_config import ThirdPayConfig
from app.libs.string_kit import RandomString
from app.libs.kuaihui.sdk import sig
import urllib.parse


class CallbackKhpay(DepositCallbackBase):
    """
    快汇支付充值回调处理
    """
    # third_config = ThirdPayConfig.KUAIHUI.value

    @classmethod
    def generate_sign(cls, form, third_config):
        """
        生成签名
        :param form: 
        :return:
        """
    
        # 调用sdk
        s = sig.Sig(third_config['secret_key'])
        param = {
            'custid': form.custid.data,
            'ordid': form.ordid.data,
            'companyname': form.companyname.data,
            'client_ordid': form.client_ordid.data,
            'channel': form.channel.data,
            'bankcode': form.bankcode.data,
            'bgreturl': form.bgreturl.data,
            'accountid': form.accountid.data,
            'accountname': form.accountname.data,
            'amount': form.amount.data,
            'remark': form.remark.data,
            'status': form.status.data,
            'message': form.message.data,
            'trans_at': form.trans_at.data,
            'created_at': form.created_at.data,
            'updated_at': form.updated_at.data,
        }

        # 取得请求url的path
        path = urllib.parse.urlparse(form.bgreturl.data).path

        current_app.logger.info('CallbackKhpay.generate_sign, param: %s, path: %s', param, path)

        return s.create("POST", path, param)

    @classmethod
    def check_sign(cls, form, third_config):
        """
        签名校验
        :param form:
        :return:
        """
        sign = cls.generate_sign(form, third_config)
        current_app.logger.info('CallbackKhpay.check_sign, sign: %s, form.sig.data: %s', sign, form.sig.data)
        return sign == form.sig.data
