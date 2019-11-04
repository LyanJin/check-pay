# -*-coding:utf8-*-
import os
import traceback
from decimal import Decimal

import requests
from flask import current_app

from app.channel.deposit_base import DepositRequestBase
from app.channel.tongyi_pay.deposit.callback import CallbackTongYiPay
from app.enums.third_enum import SdkRenderType


class DepositRequest(DepositRequestBase):

    def gen_url(self):

        # http://47.107.254.140:3020/pay/buildorder
        host = self.third_config['post_url'].strip('/')
        path = self.third_config['deposit_path'].strip('/')
        return os.path.join(host, path)

    def parse_response(self, resp, order, params:dict):
        if resp.status_code != 200:
            return dict(
                code=-100,
                msg='http请求失败，状态: %s' % resp.status_code,
                data=dict(),
            )

        data = resp.json()

        if data['retCode'] == "SUCCESS":
            return dict(
                code=0,
                msg='ok',
                data=dict(
                    render_type=SdkRenderType.URL,
                    render_content=data['payUrl']
                )
            )
            pass
        else:
            return dict(
                code=-999,
                msg='state: {}, error_message:{}'.format(data.get('retCode', 'False'),
                                                         data.get('retMsg', 'False')),
                data=dict()
            )

    def construct_request(self, order, params: dict):

        request_fields = ['merchant', 'order', 'payChannel', 'money', 'currency', 'client', 'deviceType',
                          'extraParam', 'notifyUrl', 'returnUrl', 'title', 'detail', 'sign']

        sorted_fields = sorted(request_fields)
        request_body = dict()
        for field in request_fields:
            if field == "merchant":
                request_body[field] = self.third_config['mch_id']
            elif field == "order":
                request_body[field] = order.sys_tx_id
            elif field == "payChannel":
                request_body[field] = "FLASH_PAY"
            elif field == "money":
                request_body[field] = str(int(Decimal(order.amount) * Decimal('100')))
            elif field == "currency":
                request_body[field] = "cny"
            elif field == "client":
                request_body[field] = params['client_ip']
            elif field == "deviceType":
                request_body[field] = "mobile"
            elif field == "extraParam":
                request_body[field] = ""
            elif field == "notifyUrl":
                request_body[field] = self.third_config['callback_url']
            elif field == "returnUrl":
                request_body[field] = ""
            elif field == "title":
                request_body[field] = "shopping title"
            elif field == "detail":
                request_body[field] = "shopping detail note"

        sign_str = "&".join(["{}={}".format(k, request_body[k]) for k in sorted_fields if request_body.get(k, False)])
        return request_body, sign_str

    def launch_pay(self, order, params: dict):
        url = self.gen_url()
        request_body, sign_str = self.construct_request(order, params)

        print("sign string: ", sign_str)
        print("request body: ", request_body)

        sign = CallbackTongYiPay.gen_sign(sign_str=sign_str)

        request_body['sign'] = sign

        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        try:
            current_app.logger.info('TongYi Pay, url: %s, data: %s, sign_str: %s', url, request_body, sign_str)
            resp = requests.post(url=url, data=request_body, headers=headers)
            current_app.logger.info('TongYi Pay response, status_code: %s, content: %s, headers: %s', resp.status_code,
                                    resp.text, resp.headers)
        except Exception as e:
            current_app.logger.fatal(traceback.format_exc())
            return dict(
                code=-100,
                msg="http请求失败",
                data=dict(),
            )
        return self.parse_response(resp, order, params)


