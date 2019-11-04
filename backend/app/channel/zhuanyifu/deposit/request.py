import os
import traceback
from decimal import Decimal
from urllib.parse import quote
import hmac, base64
from hashlib import sha256
import requests
from flask import current_app

from app.enums.third_enum import SdkRenderType
from app.libs.crypto import CryptoKit

from app.channel.deposit_base import DepositRequestBase
from app.libs.datetime_kit import DateTimeKit


class DepositRequest(DepositRequestBase):

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
        print(data)
        # 先签名
        chc = hmac.new(base64.b64decode(self.third_config['secret_key']), data, sha256).hexdigest()
        return chc

    def gen_rsa_sign(self, signed_data):
        """
        加密
        :return:
        """
        return CryptoKit.rsa_sign(signed_data, self.third_config['mch_private_key'])

    def gen_url(self, *args, **kwargs):
        host = self.third_config['post_url'].strip('/')
        path = self.third_config['withdraw_path'].strip('/')
        return os.path.join(host, path)

    def launch_pay(self, order, params: dict):
        """
        专一付 充值请求
        :param order:
        :param params:
        :return:
        """
        post_data_json = '{'
        for field in ["type", "channel", "order", "currency", "amount", "time", "timeout", "product", "client",
                      "remark", "result_url", "account_type", "no"]:
            if field == 'type':
                post_data_json += '"{}":"{}",'.format(field, "7")
            elif field == "channel":
                post_data_json += '"{}":"{}",'.format(field, "0")
            elif field == "order":
                post_data_json += '"{}":"{}",'.format(field, order.sys_tx_id)
            elif field == "currency":
                post_data_json += '"{}":{},'.format(field, 1)
            elif field == "amount":
                if isinstance(order.amount, Decimal):
                    post_data_json += '"{}":{},'.format(field, order.amount.quantize(Decimal("0.00")))
                else:
                    post_data_json += '"{}":{},'.format(field, Decimal(str(order.amount)).quantize(Decimal("0.00")))
            elif field == 'time':
                post_data_json += '"{}":{},'.format(field, DateTimeKit.get_cur_timestamp())
            elif field == 'timeout':
                post_data_json += '"{}":{},'.format(field, 3600)
            elif field == 'product':
                post_data_json += '"product":{'
                for item in ["subject", "body"]:
                    if item == "subject":
                        post_data_json += '"{}":"{}"'.format(item, "subject")
                    # else:
                    #     post_data_json += '"{}":"{}"'.format(item, "body")
                        post_data_json += '},'
            # elif field == "remark":
            #     post_data_json += '"{}":"{}",'.format(field, "remark")
            elif field == "result_url":
                post_data_json += '"{}":"{}",'.format(field, "http://localhost.com")
            elif field == "account_type":
                # todo 只网银和快 捷页面版才 用
                post_data_json += '"{}":{}'.format(field, 1)
            # elif field == "no":
            #     # todo 只当快捷时才用
            #     post_data_json += '"{}":"{}"'.format(field, "64423498734599")
        post_data_json += "}"
        print(post_data_json, "^^^^^^^^^^^^^^^^^^^")
        header_str = "Application=" + quote(self.third_config['app_id'], safe="", encoding="utf8") + "&Content-Type=" + quote("application/json", safe="", encoding="utf8") + "&Event=" + quote("Charge", safe="", encoding="utf8")

        header_fields = ['ChinaRailway-Application: ' + self.third_config['app_id'],
                         "ChinaRailway-Event: Charge",
                         "Content-Type: application/json; charset=utf-8"]
        headers = dict()
        for s in header_fields:
            k, v = s.split(': ')
            headers[k] = v

        s1 = self.generate_sign(header_str.encode('utf8'), post_data_json.encode('utf8'))
        s2 = self.gen_rsa_sign(s1.encode('utf8'))
        sign = '.'.join([s1, s2.decode()])
        url = self.gen_url()
        headers['ChinaRailway-Signature'] = sign
        kwargs = dict(headers=headers, verify=False)

        code = 0
        msg = ""
        render_content = None

        try:

            current_app.logger.info('zhuanyifu deposit, url: %s, kwargs: %s, data: %s', url, kwargs, post_data_json)

            rsp = requests.post(url, data=post_data_json.encode('utf8'), **kwargs)

            current_app.logger.info('zhuanyifu deposit, status_code: %s, content: %s', rsp.status_code, rsp.text)

        except Exception as e:
            current_app.logger.fatal(traceback.format_exc())
            code = -1
            msg = "http请求异常"

        else:

            print(rsp.json(), rsp.text)

            if rsp.status_code != 200:
                code = -2
                msg = rsp.text
            else:
                credential = rsp.json().get('credential', '')
                if credential:
                    content = credential.get('content', '')
                    if content:
                        # 正确的数据
                        render_content = content
                    else:
                        code = -3
                        msg = rsp.text
                else:
                    code = -4
                    msg = rsp.text

        # 统一返回值
        return dict(
            code=code,             # 错误码，code=0是没有错误
            msg=msg,             # 当code不等于0时，填写错误提示信息
            data=dict(
                render_type=SdkRenderType.FORM,      # 类型
                render_content=render_content,               # 内容
            ),
        )



