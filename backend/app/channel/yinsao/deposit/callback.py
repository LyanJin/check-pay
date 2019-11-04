from flask import current_app

from app.channel.deposit_base import DepositCallbackBase
from app.enums.third_config import ThirdPayConfig
from app.libs.string_kit import RandomString


class CallbackYinSao(DepositCallbackBase):
    """
    立马敷充值回调处理
    """
    third_config = ThirdPayConfig.YINSAO_DEPOSIT.value

    @classmethod
    def generate_sign(cls, request_fields_str):
        """
        生成签名
        :param merchant_id: 通道分配给我们的商户ID
        :param channel_tx_id: 通道交易ID(由通道侧生成)
        :param tx_amount: 实际支付金额
        :return:
        """
        sign_str = request_fields_str + "&key="
        sign_str += cls.third_config['secret_key']
        current_app.logger.info('sign data: %s', sign_str)
        return RandomString.gen_md5_string(sign_str.encode("utf8")).upper()

    @classmethod
    def check_sign(cls, post_sign, gen_sign):
        """
        签名校验
        :param form:
        :return:
        """
        current_app.logger.info('post_sign: %s, gen_sign: %s', post_sign, gen_sign)
        return post_sign == gen_sign
