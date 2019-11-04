import hashlib

from app.channel.deposit_base import DepositCallbackBase
from app.enums.third_config import ThirdPayConfig


class CallbackEpayTong(DepositCallbackBase):
    third_config = ThirdPayConfig.EpayTong_PAY_DEPOSIT.value

    @classmethod
    def gen_sign(cls, sign_str):
        m = hashlib.sha1()
        m.update(sign_str.encode('utf8'))
        sign = m.hexdigest().upper()
        return sign

    @classmethod
    def check_sign(cls, sign, request_str):
        m = hashlib.sha1()
        m.update(request_str.encode('utf8'))
        s2 = m.hexdigest().upper()
        print("sign:", sign, s2)
        return sign == s2


