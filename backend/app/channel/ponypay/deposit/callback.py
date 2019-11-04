from app.channel.deposit_base import DepositCallbackBase
from app.enums.third_config import ThirdPayConfig
from app.libs.string_kit import RandomString


class CallbackPonypay(DepositCallbackBase):
    """
    立马敷充值回调处理
    """
    third_config = ThirdPayConfig.LIMAFU_95632.value

    @classmethod
    def generate_sign(cls, merchant_id, channel_tx_id, tx_amount):
        """
        生成签名
        :param merchant_id: 通道分配给我们的商户ID
        :param channel_tx_id: 通道交易ID(由通道侧生成)
        :param tx_amount: 实际支付金额
        :return:
        """
        sign_str = "".join([merchant_id, channel_tx_id, tx_amount])
        sign_str += cls.third_config['secret_key']
        return RandomString.gen_md5_string(sign_str.encode("gb2312")).lower()

    @classmethod
    def check_sign(cls, form):
        """
        签名校验
        :param form:
        :return:
        """
        sign = cls.generate_sign(form.merchant_id.data, form.orderid.data, form.money.data)
        return sign == form.sign.data
