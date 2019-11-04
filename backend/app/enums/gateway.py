from app.enums.base_enum import BaseEnum
from config import MerchantEnum


class GatewayMerchantConfig(BaseEnum):
    TEST_API = dict(
        secret_key="=sCOYELK9zjkD^XGHA-N(Uq5d0RBvtS!JP1*+p#62crQ7)xI4M%&WTyVf3he8noi",
        white_ips=[
            '127.0.0.1',
            # 运营办公室IP
            '103.119.131.16',
            # 测试环境IP
            '18.162.236.151',
            '18.162.143.27',
            '18.162.123.175',
            # 正式环境服务器IP
            '18.162.55.13',
            '18.162.58.26',
            '18.162.154.29',
        ],
    )

    HAOMEN = dict(
        secret_key="majxhUt)Nf&3l68%keDO=TpiK7bz^wJQWsRog2MHFvLSBPVquG-rZ9yIc#E4(A5*",
        white_ips=[
            "104.215.192.114",
            "137.116.134.154",
        ],
    )

    @classmethod
    def get_config(cls, merchant: MerchantEnum):
        return getattr(cls, merchant.name).value

    @classmethod
    def get_secret(cls, merchant):
        return cls.get_config(merchant)['secret_key']

    @classmethod
    def get_white_ips(cls, merchant):
        return cls.get_config(merchant)['white_ips']
