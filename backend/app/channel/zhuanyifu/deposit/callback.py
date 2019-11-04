from app.channel.deposit_base import DepositCallbackBase
from app.enums.third_config import ThirdPayConfig
from app.libs.crypto import CryptoKit


class CallbackZYF(DepositCallbackBase):
    """
    专一付 代收回调
    """
    third_config = ThirdPayConfig.ZHUANYIFU_DEPOSIT_11159.value

    # @classmethod
    # def generate_sign(cls, merchant_id, channel_tx_id, tx_amount):
    #     """
    #     生成签名
    #     :param merchant_id: 通道分配给我们的商户ID
    #     :param channel_tx_id: 通道交易ID(由通道侧生成)
    #     :param tx_amount: 实际支付金额
    #     :return:
    #     """
    #     sign_str = "".join([merchant_id, channel_tx_id, tx_amount])
    #     sign_str += cls.third_config['secret_key']
    #     return RandomString.gen_md5_string(sign_str.encode("gb2312")).lower()

    @classmethod
    def check_sign(cls, pp, channel_config):
        """
        签名校验
        :param pp 签名数据:
        :param channel_config 通道配置:
        :return:
        """
        # flag = CryptoKit.rsa_verify(pp[1], pp[0], conf['plat_public_key'])
        flag = CryptoKit.rsa_verify(pp[1], pp[0], channel_config.channel_enum.conf['plat_public_key'])
        return flag