import hashlib


class CallbackEpayTong:

    @classmethod
    def generate_sign(cls, sign_str):
        m = hashlib.sha1()
        m.update(sign_str.encode('utf8'))
        sign = m.hexdigest().upper()
        return sign

    @classmethod
    def check_sign(cls, sign, sign_str):
        m = hashlib.sha1()
        m.update(sign_str.encode('utf8'))
        s2 = m.hexdigest().upper()
        return sign == s2
