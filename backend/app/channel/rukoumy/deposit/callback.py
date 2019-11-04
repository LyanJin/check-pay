import hashlib

from flask import current_app

from app.channel.deposit_base import DepositCallbackBase
from app.enums.third_config import ThirdPayConfig


class CallbackRuKouMy(DepositCallbackBase):
    third_config = ThirdPayConfig.RUKOUMY_DEPOSIT.value

    @classmethod
    def gen_sign(cls, sign_str):
        sign_str += "&{}={}".format("key", cls.third_config['secret_key'])
        print(sign_str, "&&&&&&&&&&&&&&&&")
        m = hashlib.md5(sign_str.encode('utf8'))
        sign = m.hexdigest().upper()
        return sign

    @classmethod
    def check_sign(cls, sign, sign_str):
        # cls.third_config['secret_key']
        sign_str += "&{}={}".format("key", cls.third_config['secret_key'])
        m = hashlib.md5(sign_str.encode('utf8'))
        s2 = m.hexdigest().upper()
        print(sign, s2, sign_str)
        return sign == s2