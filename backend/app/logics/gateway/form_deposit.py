"""
API表单校验
"""
from app.enums.gateway import GatewayMerchantConfig
from app.logics.gateway.sign_check import GatewaySign
from app.models.user import User
from config import MerchantEnum


class GatewayFormChecker:

    def __init__(self, merchant: MerchantEnum):
        self.merchant = merchant

    def verify_sign(self, sign, params: dict):
        """
        校验签名
        :param sign:
        :param params:
        :return:
        """
        return GatewaySign(self.merchant).verify_sign(sign, params)

    def get_sign_str(self, params):
        """
        获得签名前的字符串
        :param params:
        :return:
        """
        return GatewaySign(self.merchant).join_sign_str(params)

    def get_white_ips(self):
        """
        获取白名单
        :return:
        """
        return GatewayMerchantConfig.get_white_ips(self.merchant)

    def verify_ip(self, ip):
        """
        IP白名单校验
        :param ip:
        :return:
        """
        return ip in GatewayMerchantConfig.get_white_ips(self.merchant)

    def get_fake_user(self, account):
        """
        获取用户对象，如果不存在则注册
        :param account:
        :return:
        """
        return User.generate_model(self.merchant, account=account or '')
