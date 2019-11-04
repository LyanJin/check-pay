"""
签名
"""
from app.enums.channel import ChannelConfigEnum
from app.libs.string_kit import RandomString


class SignBase:
    def __init__(self, channel_enum: ChannelConfigEnum):
        self.channel_enum = channel_enum
        self.channel_conf = channel_enum.conf

    def get_secret_key(self):
        return self.channel_conf.secret_key

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
        sign = RandomString.gen_md5_string(raw_str.encode('utf8')).upper()
        return sign

    def check_sign(self, params: dict, sign):
        """
        签名校验
        :param params:
        :param sign:
        :return:
        """
        return self.generate_sign(params) == sign

    def check_ip(self, client_ip):
        """
        IP白名单校验
        :param client_ip:
        :return:
        """
        return self.channel_conf["white_ip"] and client_ip in self.channel_conf["white_ip"]
