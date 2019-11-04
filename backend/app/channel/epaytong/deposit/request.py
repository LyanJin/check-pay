import os
import traceback
from decimal import Decimal

import requests
from flask import current_app

from app.channel.deposit_base import DepositRequestBase
from app.channel.epaytong.deposit.callback import CallbackEpayTong
from app.enums.third_enum import SdkRenderType
from app.enums.trade import PayMethodEnum


class DepositRequest(DepositRequestBase):

    def gen_url(self, order):
        mch_id = self.third_config['mch_id']
        host = self.third_config['post_url'].strip('/')
        path = self.third_config['deposit_path'].strip('/').format(mch_id, order.sys_tx_id)
        return os.path.join(host, path)

    def construct_request(self, order, params: dict):
        pay_params = {
            PayMethodEnum.ZHIFUBAO_SAOMA: dict(defaultbank="ALIPAY", isApp="web", paymethod="directPay",
                                               render_type=SdkRenderType.HTML),
            PayMethodEnum.ZHIFUBAO_H5: dict(defaultbank="ALIPAY", isApp="H5", paymethod="directPay",
                                            render_type=SdkRenderType.HTML),
            PayMethodEnum.YUNSHANFU: dict(defaultbank="UNIONQRPAY", isApp="web", paymethod="directPay",
                                          render_type=SdkRenderType.HTML),
            PayMethodEnum.WEIXIN_SAOMA: dict(defaultbank="WXPAY", isApp="web", paymethod="directPay",
                                             render_type=SdkRenderType.HTML),
            PayMethodEnum.WEIXIN_H5: dict(defaultbank="WXPAY", isApp="H5", paymethod="directPay",
                                          render_type=SdkRenderType.HTML),
            PayMethodEnum.YINLIAN_KUAIJIE: dict(defaultbank="EASYQUICK", isApp="web", paymethod="bankPay",
                                                render_type=SdkRenderType.HTML),
        }

        payment_method = self.channel_enum.conf['payment_method']
        request_fields = ['body', 'buyerEmail', 'charset', 'defaultbank', 'isApp', 'merchantId', 'notifyUrl',
                          'orderNo', 'paymentType', 'paymethod', 'returnUrl', 'riskItem', 'service', 'sellerEmail',
                          'title', 'totalFee', 'signType', 'sign']
        sorted_params = sorted(request_fields)

        request_body = {}

        for field in request_fields:
            if field == "body":
                request_body[field] = "body"
            elif field == "buyerEmail":
                request_body[field] = "abc123@163.com"
            elif field == "charset":
                request_body[field] = "UTF-8"
            elif field == "defaultbank":
                request_body[field] = pay_params[payment_method].get(field, "")
            elif field == "isApp":
                request_body[field] = pay_params[payment_method].get(field, "")
            elif field == "merchantId":
                request_body[field] = self.third_config['mch_id']
            elif field == "notifyUrl":
                request_body[field] = self.third_config["callback_url"]
            elif field == "orderNo":
                request_body[field] = order.sys_tx_id
            elif field == "paymentType":
                request_body[field] = "1"
            elif field == "paymethod":
                request_body[field] = pay_params[payment_method].get(field, "")
            elif field == "returnUrl":
                request_body[field] = self.third_config["return_url"]
            elif field == "riskItem":
                request_body[field] = ""
            elif field == "service":
                request_body[field] = "online_pay"
            elif field == "sellerEmail":
                request_body[field] = "sellerEmail"
            elif field == "title":
                request_body[field] = "epay tong"
            elif field == "totalFee":
                request_body[field] = Decimal(str(order.amount))

        sign_str = "&".join(["{}={}".format(k, request_body[k]) for k in sorted_params if request_body.get(k, False)])
        sign_str += self.third_config['secret_key']

        print("sign string: ", sign_str)
        print("request body: ", request_body)

        render_type = pay_params[payment_method]['render_type']

        return request_body, sign_str, render_type

    def launch_pay(self, order, params: dict):

        url = self.gen_url(order)

        request_body, sign_str, render_type = self.construct_request(order, params)

        sign = CallbackEpayTong.gen_sign(sign_str=sign_str)

        request_body["sign"] = sign
        request_body["signType"] = "SHA"

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        code = 0
        msg = ''
        try:
            current_app.logger.info(
                'Epay Tong deposit request url: {}, data: {}, headers:{}'.format(url, request_body, headers))
            kwargs = dict(headers=headers, verify=False)
            resp = requests.post(url=url, data=request_body, **kwargs)
            current_app.logger.info('Epay Tong deposit response, status_code: %s, content: %s', resp.status_code,
                                     resp.text)
        except Exception as e:
            current_app.logger.fatal(traceback.format_exc())
            code = -1
            msg = "http请求异常"
            # 统一返回值

        if resp.status_code != 200:
            code = int(resp.status_code)
            msg = resp.text

        # if resp.respCode [S0001, F9999]  respMessage [请求已成功执行, 服务器系统繁忙]

        return dict(
            code=code,  # 错误码，code=0是没有错误
            msg=msg,  # 当code不等于0时，填写错误提示信息
            data=dict(
                render_type=render_type,  # 类型
                render_content=resp.text,  # 内容
            ),
        )
