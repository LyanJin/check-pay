from app.libs.string_kit import RandomString
from app.channel.withdraw_base import ProxyPayCallback


class WithdrawCallbackYinSao(ProxyPayCallback):

    @staticmethod
    def generate_sign(request_fields_str, third_config):
        """
        生成签名
        :param merchant_id: 通道分配给我们的商户ID
        :param channel_tx_id: 通道交易ID(由通道侧生成)
        :param tx_amount: 实际支付金额
        :return:
        """
        sign_str = request_fields_str + "&key="
        sign_str += third_config['secret_key']
        return RandomString.gen_md5_string(sign_str.encode("utf8")).upper()
    @staticmethod
    def check_sign(self, corderid, money, sign):
        return sign == self.generate_sign(corderid, money)
