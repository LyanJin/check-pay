# -*-coding:utf8-*-
import os
import traceback
from decimal import Decimal

import requests
from flask import current_app

from app.channel.deposit_base import DepositRequestBase
from app.channel.jinzuan.deposit.callback import CallbackJinZuan
from app.enums.third_enum import SdkRenderType
from app.enums.trade import PayMethodEnum
from app.libs.datetime_kit import DateTimeKit


class DepositRequest(DepositRequestBase):

    def gen_url(self):
        url_header = ["merchantId", "timestamp", "signatureMethod", "signatureVersion"]
        url_params = dict()
        for h_field in url_header:
            if h_field == "merchantId":
                url_params[h_field] = self.third_config['mch_id']
            elif h_field == "timestamp":
                url_params[h_field] = DateTimeKit.get_cur_timestamp(bit=1000)
            elif h_field == "signatureMethod":
                url_params[h_field] = "HmacSHA256"
            elif h_field == "signatureVersion":
                url_params[h_field] = "1"

        host = self.third_config['post_url'].strip('/')
        path = self.third_config['deposit_path'].strip('/')
        return os.path.join(host, path), url_params

    def parse_response(self, resp, order, params: dict):
        if resp.status_code != 200:
            return dict(
                code=-100,
                msg='http请求失败，状态: %s' % resp.status_code,
                data=dict(),
            )

        data = resp.json()

        if str(data['status']) == "1":
            return dict(
                code=0,
                msg='ok',
                data=dict(
                    render_type=SdkRenderType.URL,
                    render_content=data['break_url']
                )
            )
        else:
            return dict(
                code=-999,
                msg='state: {}, error_message:{}'.format(data.get('status', 'False'),
                                                         data.get('error_msg', 'False')),
                data=dict()
            )

    def construct_request(self, order, params: dict):

        request_fields = ['jUserId', 'jUserIp', 'jOrderId', 'orderType', 'payWay',
                          'amount', 'currency', 'jExtra', 'notifyUrl']

        pay_params = {
            PayMethodEnum.ZHIFUBAO_SAOMA: dict(channel="AliPay", render_type=SdkRenderType.URL),
            PayMethodEnum.WEIXIN_SAOMA: dict(channel="WechatPay", render_type=SdkRenderType.URL)
        }

        payment_method = self.channel_enum.conf['payment_method']

        request_body = dict()
        for field in request_fields:
            if field == "company_id":
                request_body[field] = self.third_config['mch_id']
            elif field == "jOrderId":
                request_body[field] = order.sys_tx_id
            elif field == "orderType":
                request_body[field] = "1"
            elif field == "payWay":
                request_body[field] = pay_params[payment_method]['channel']
            elif field == "amount":
                request_body[field] = "{:.2f}".format(float(Decimal(str(order.amount))))
            elif field == "jUserId":
                request_body[field] = str(params['user'].uid)
            elif field == "jUserIp":
                request_body[field] = params['client_ip']
            elif field == "currency":
                request_body[field] = "CNY"
            elif field == "jExtra":
                request_body[field] = "0"
            elif field == "notifyUrl":
                request_body[field] = self.third_config['callback_url']

        return request_body

    def launch_pay(self, order, params: dict):
        url, url_params = self.gen_url()
        request_body, request_field = self.construct_request(order, params)

        r_params = url_params.copy()
        r_params.update(request_body)

        sign = CallbackJinZuan.gen_sign(sign_str=sign_str)

        request_body['key'] = sign

        headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8"
        }
        try:
            current_app.logger.error('GPay, url: %s, data: %s, sign_str: %s， headers: %s', url, request_body, sign_str,
                                     headers)
            resp = requests.post(url=url, data=request_body, headers=headers)
            current_app.logger.info('GPay response, status_code: %s, content: %s, headers: %s', resp.status_code,
                                    resp.text, resp.headers)
        except Exception as e:
            current_app.logger.fatal(traceback.format_exc())
            return dict(
                code=-100,
                msg="http请求失败",
                data=dict(),
            )
        return self.parse_response(resp, order, params)
