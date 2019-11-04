from flask import current_app

from app.channel.sign_base import SignBase
from app.libs.string_kit import RandomString


class DepositCallbackJifu(SignBase):
    """
    极付充值回调处理
    """
    def join_sign_str(self, params: dict):
        keys = sorted(list(params.keys()))
        return '&'.join(["=".join(map(str, [k, params[k]])) for k in keys if params[k]])

    def generate_sign(self, params: dict):
        """
        生成签名
        :param params:
        :return:
        """
        raw_str = self.join_sign_str(params)
        raw_str += '&key=' + self.get_secret_key()
        # current_app.logger.info('raw_str: %s', raw_str)
        # current_app.logger.info('raw_str utf8: %s', raw_str.encode('utf8'))
        sign = RandomString.gen_md5_string(raw_str.encode('utf8')).upper()
        return sign

    def check_sign(self, params: dict, sign):
        """
        签名校验
        :param params:
        :param sign:
        :return:
        """
        _sign = self.generate_sign(params)
        # current_app.logger.info('_sign: %s, sign: %s', _sign, sign)
        return _sign == sign
