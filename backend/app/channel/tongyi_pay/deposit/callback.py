import hashlib

from flask import current_app

from app.channel.deposit_base import DepositCallbackBase
from app.enums.third_config import ThirdPayConfig


class CallbackTongYiPay(DepositCallbackBase):
    third_config = ThirdPayConfig.TONGYI_PAY_DEPOSIT.value

    @classmethod
    def gen_sign(cls, sign_str):
        sign_str += "&{}={}".format("key", cls.third_config['secret_key'])
        m = hashlib.md5(sign_str.encode('utf8'))
        sign = m.hexdigest().upper()
        return sign

    @classmethod
    def check_sign(cls, sign, sign_str):
        sign_str += "&{}={}".format("key", cls.third_config['secret_key'])
        m = hashlib.md5(sign_str.encode('utf8'))
        s2 = m.hexdigest().upper()
        if not sign == s2:
            current_app.logger.error("callback sign: %s, gen sign: %s", sign, s2)
        return sign == s2
