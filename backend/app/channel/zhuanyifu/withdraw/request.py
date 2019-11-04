# -*-coding:utf8-*-
"""
立马付接口代付API
"""
import traceback
from urllib.parse import quote
import hmac, base64
from hashlib import sha256
import requests
from flask import current_app

from app.enums.channel import ChannelConfigEnum
from app.enums.trade import PaymentBankEnum
from app.libs.crypto import CryptoKit
from app.libs.datetime_kit import DateTimeKit
from app.channel.withdraw_base import ProxyPayRequest

BANK_CODE_DICT = {
    PaymentBankEnum.ZHONGGUO.bank_code: '10003',
    PaymentBankEnum.GONGSHANG.bank_code: '10001',
    PaymentBankEnum.JIANSHE.bank_code: '10004',
    PaymentBankEnum.NONGYE.bank_code: '10002',
    PaymentBankEnum.YOUZHENG.bank_code: '10006',
    PaymentBankEnum.ZHAOSHANG.bank_code: '11005',
    PaymentBankEnum.PUFA.bank_code: '11009',
    PaymentBankEnum.MINSHENG.bank_code: '11004',
    PaymentBankEnum.PINGAN.bank_code: '11008',
    PaymentBankEnum.HUAXIA.bank_code: '11003',
    PaymentBankEnum.ZHONGXIN.bank_code: '11001',
    PaymentBankEnum.GUANGDA.bank_code: '11002',
    PaymentBankEnum.XINGYE.bank_code: '11006',
    PaymentBankEnum.GUANGFA.bank_code: '11007',
    PaymentBankEnum.JIAOTONG.bank_code: '10005',
}


class RequestZhuanYiFu(ProxyPayRequest):
    """
    立马付代付请求
    """

    header_prefix = 'ChinaRailway-'

    def get_headers(self):
        header_fields = ['ChinaRailway-Application: ' + self.third_config['app_id'],
                         "ChinaRailway-Event: Pay",
                         "Content-Type: application/json; charset=utf-8"]
        header_dict = dict()
        for s in header_fields:
            k, v = s.split(': ')
            header_dict[k] = v

        header_str = "Application=" + quote(self.third_config['app_id'], safe="",
                                            encoding="utf8") + "&Content-Type=" + quote("application/json", safe="",
                                                                                        encoding="utf8") + "&Event=" + quote(
            "Pay", safe="", encoding="utf8")

        return header_dict, header_str.encode('utf8')

    def get_body(self, params_dict):
        body = '{"type":"%s","channel":"%s","order":"%s","currency":%s,"amount":"%s","time":"%s","timeout":"%s","product":{"subject":"%s","body":"%s"},"account_type":%s,"no":"%s","name":"%s"}' \
               % (str(1), BANK_CODE_DICT[params_dict['bank_code']], params_dict['tx_id'], 1,
                  str(params_dict['amount']), DateTimeKit.get_cur_timestamp(), 3600, "subject", "body", 1,
                  params_dict['bank_number'], params_dict['bank_account']
                  )
        return body

    def generate_sign(self, header, body):
        """
        生成签名
        data = 头部（header） + JSON 字符串 (utf-8 编码)
        s1 = hs256(hs_key, data)（HexString十六进制字符串） HMAC-SHA256
        s2 = rs256(vendor_private_key, s1)（Base64String Base64字符串） RSA-SHA256
        签名 = s1.s2
        注：HTTP 方式需要分别做 urlencode 再用点号连接
        注：提交数据用商户私钥签名，返回数据用平台公钥
        """
        data = header + body
        # 先签名
        chc = hmac.new(base64.b64decode(self.third_config['secret_key']), data, sha256).hexdigest()
        return chc

    def gen_rsa_sign(self, signed_data):
        """
        加密
        :return:
        """
        return CryptoKit.rsa_sign(signed_data, self.third_config['mch_private_key'])

    def verify_rsa_sign(self, sign, encrypt_data):
        """
        验证签名
        :param sign:
        :param encrypt_data:
        :return:
        """
        return CryptoKit.rsa_verify(sign, encrypt_data, self.third_config['mch_private_key'].encode("utf8"))

    def construct_request(self, params_dict: dict):
        """
        组织请求数据
        """
        header, header_str = self.get_headers()
        body = self.get_body(params_dict)

        s1 = self.generate_sign(header_str, body.encode('utf8'))
        s2 = self.gen_rsa_sign(s1.encode('utf8'))

        code_s1 = s1
        code_s2 = s2.decode()

        sign = '.'.join([code_s1, code_s2])
        return header, body, sign

    def parse_response(self, resp):
        """
        解析响应
        status	状态	1：正确; 0：错误，此状态时，message中会有提示信息！
        data	数据	[{"corderid":"xxx","status":"1","message":"错误信息！"},…]
            Status:1 为成功建立订单，
            Status：0 为未建立订单，message为错误信息。
        message	提示信息	 错误提示信息
        data2	交易流水号	 预留
        """

        if resp.status_code != 200:
            return dict(
                code=-100,
                msg='http请求失败，状态: %s' % resp.status_code,
                data=dict(),
            )
        json_data = resp.json()
        if int(json_data.get('status', -1)) not in ['0', '1', '2']:
            return dict(
                code=-999,
                msg=json_data['message'],
                data=dict(),
            )

        # if str(json_data['status']) == '0':
        #     # "代付： 代出款"
        #     return dict(
        #         code=0,
        #         msg="待代付",
        #         data=item
        #     )

        item = json_data['data'][0]
        # if str(item['status']) == '1':
        #     # "代付： 支付成功"
        #     return dict(
        #         code=0,
        #         msg="支付成功",
        #         data=item
        #     )

        if str(item['status']) == '2':
            # "代付： 支付失败"
            return dict(
                code=-1,
                msg="支付失败",
                data=item
            )

        return dict(
            code=0,
            msg="待代付",
            data=item
        )

    def launch_pay(self, params_dict: dict):
        """
        发起支付
        :return:
        """
        headers, body, sign = self.construct_request(params_dict)

        url = self.gen_url()
        headers['ChinaRailway-Signature'] = sign

        kwargs = dict(headers=headers, verify=False)

        current_app.logger.info('zhuanyifu withdraw, url: %s, data: %s', url, body)
        try:
            rsp = requests.post(url, data=body.encode('utf8'), **kwargs)
            current_app.logger.info('zhuanyifu withdraw, status_code: %s, content: %s', rsp.status_code, rsp.text)
        except Exception as e:
            current_app.logger.fatal(traceback.format_exc())
            return dict(
                code=-100,
                msg="http请求失败",
                data=dict())

        return self.parse_response(rsp)


if __name__ == '__main__':
    _data = {
        "tx_id": "12334543",  # 商户代付订单号；
        "amount": "405.00",  # 代付金额，请加手续费5元，实际到账减5元
        "bank_name": "中国工商银行",  # 银行名称
        "bank_account": "王大锤",  # 用户在银行的姓名
        "bank_number": "633992923483243247327",  # 银行账号
        "bank_address": "开户行地址"  # 例如：中国银行XXXX支行
    }

    rst, _tx_id = RequestZhuanYiFu(ChannelConfigEnum.CHANNEL_1001).launch_pay(**_data)
    print(rst, _tx_id)
