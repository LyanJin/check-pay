from app.libs.string_kit import RandomString
from app.channel.withdraw_base import ProxyPayCallback


class WithdrawCallbackPonypay(ProxyPayCallback):

    def generate_sign(self, corderid, money):
        """
        merchant_id	商户编号	是	 商户号
        corderid	订单号	是	 商户订单号
        money	订单金额	是	 订单金额
        status	交易状态	否	1 为已成功，2,为作废（金额退回）。
        sign	签名	否

        string  parastring =  merchant_id + corderid + money + key;
        sign=MD5(parastring);
        """
        params_string = ''.join([self.third_config['mch_id'], corderid, str(money), self.third_config['secret_key']])
        return RandomString.gen_md5_string(params_string.encode("gb2312")).upper()

    def check_sign(self, corderid, money, sign):
        return sign == self.generate_sign(corderid, money)
