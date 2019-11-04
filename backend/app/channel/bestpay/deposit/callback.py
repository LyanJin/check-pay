import hashlib

from app.channel.deposit_base import DepositCallbackBase
from app.enums.third_config import ThirdPayConfig


class CallbackBestPay(DepositCallbackBase):
    third_config = ThirdPayConfig.BESTPAY_DEPOSIT.value

    @classmethod
    def gen_sign(cls, sign_str):
        if sign_str == '':
            sign_str = cls.third_config['secret_key']
        else:
            sign_str = sign_str + cls.third_config['secret_key']
        m = hashlib.sha256()
        m.update(sign_str.encode('utf8'))
        sign = m.hexdigest().lower()
        return sign

    @classmethod
    def check_sign(cls, sign, request_str):
        m = hashlib.sha256()
        m.update(request_str.encode('utf8'))
        s2 = m.hexdigest().lower()
        print("sign:", sign, s2)
        return sign == s2