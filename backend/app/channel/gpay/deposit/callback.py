import hashlib

from flask import current_app

from app.channel.deposit_base import DepositCallbackBase
from app.enums.third_config import ThirdPayConfig


class CallbackGpay(DepositCallbackBase):
    third_config = ThirdPayConfig.GPAY_DEPOSIT.value

    @classmethod
    def gen_sign(cls, sign_str):
        key_md5 = hashlib.md5(cls.third_config['secret_key'].encode('utf-8')).hexdigest()
        key_md5 += sign_str
        m = hashlib.md5(key_md5.encode('utf-8'))
        sign = m.hexdigest()
        return sign

    @classmethod
    def check_sign(cls, sign, sign_str):

        key_md5 = hashlib.md5(cls.third_config['secret_key'].encode('utf-8')).hexdigest()
        key_md5 += sign_str
        m = hashlib.md5(key_md5.encode('utf-8'))
        s2 = m.hexdigest()

        if not sign == s2:
            current_app.logger.error("resp sign: %s, gen sign: %s", sign, s2)
        return sign == s2

    @classmethod
    def _hex(cls, sign_str):
        a = []
        chars = '0123456789abcdef'
        for i in range(0, len(sign_str)):
            b = sign_str[i] & 0xff
            a.append(str(chars[b >> 4]))
            a.append(str(chars[b & 0x0f]))
        return "".join(a)
