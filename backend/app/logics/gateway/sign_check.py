from app.enums.gateway import GatewayMerchantConfig
from app.libs.string_kit import RandomString
from config import MerchantEnum


class GatewaySign:

    def __init__(self, merchant: MerchantEnum):
        self.merchant = merchant

    @property
    def secret_key(self):
        return GatewayMerchantConfig.get_secret(self.merchant)

    @classmethod
    def join_sign_str(cls, params: dict):
        keys = sorted(list(params.keys()))
        return '&'.join(["=".join(map(str, [k, params[k]])) for k in keys])

    def generate_sign(self, params: dict):
        """
        生成签名
        :param params:
        :return:
        """
        raw_str = self.join_sign_str(params)
        raw_str += '&secret_key=' + self.secret_key
        print('raw_str:', raw_str)
        sign = RandomString.gen_md5_string(raw_str.encode('utf8'))
        print('sign:', sign)
        return sign

    def verify_sign(self, sign, params: dict):
        """
        校验签名
        :param sign:
        :param params:
        :return:
        """
        print('verify_sign:', sign)
        return sign == self.generate_sign(params)


if __name__ == '__main__':
    from app.logics.gateway.sign_demo import SignDemo
    sign1 = SignDemo.test()

    data = SignDemo.get_params()
    key = SignDemo.get_secret_key()

    GatewayMerchantConfig.HAOMEN.value['secret_key'] = key
    sign_checker = GatewaySign(MerchantEnum.HAOMEN)
    sign2 = sign_checker.generate_sign(data)
    assert sign1 == sign2
    sign_checker.verify_sign(sign1, data)
    sign_checker.verify_sign(sign2, data)
