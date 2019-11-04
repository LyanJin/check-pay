# -*-coding:utf8-*-
import os
import traceback
from decimal import Decimal

import requests
from flask import current_app

from app.channel.deposit_base import DepositRequestBase
from app.channel.gpay.deposit.callback import CallbackGpay
from app.enums.third_enum import SdkRenderType


class DepositRequest(DepositRequestBase):

    def gen_url(self):
        host = self.third_config['post_url'].strip('/')
        path = self.third_config['deposit_path'].strip('/')
        return os.path.join(host, path)

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

        request_fields = ['company_id', 'bank_id', 'amount', 'company_order_num', 'company_user',
                          'estimated_payment_bank', 'deposit_mode',
                          'group_id', 'web_url', 'memo', 'note', 'note_model', 'key', 'terminal', 'client_ip']

        request_body = dict()
        for field in request_fields:
            if field == "company_id":
                request_body[field] = self.third_config['mch_id']
            elif field == "company_order_num":
                request_body[field] = order.sys_tx_id
            elif field == "bank_id":
                request_body[field] = ""
            elif field == "estimated_payment_bank":
                request_body[field] = ""
            elif field == "amount":
                request_body[field] = "{:.2f}".format(float(Decimal(str(order.amount))))
            elif field == "company_user":
                request_body[field] = str(params['user'].uid)
            elif field == "client_ip":
                request_body[field] = params['client_ip']
            elif field == "deposit_mode":
                request_body[field] = "38"
            elif field == "group_id":
                request_body[field] = "0"
            elif field == "web_url":
                request_body[field] = "http://www.epay.com"
            elif field == "note":
                request_body[field] = ""
            elif field == "note_model":
                request_body[field] = "2"
            elif field == "terminal":
                request_body[field] = "2"
            elif field == "memo":
                request_body[field] = ""

        sign_str = ""
        for k in request_fields[:-3]:
            sign_str += request_body[k]
        return request_body, sign_str

    def launch_pay(self, order, params: dict):
        url = self.gen_url()
        request_body, sign_str = self.construct_request(order, params)

        print("sign string: ", sign_str)
        print("request body: ", request_body)

        sign = CallbackGpay.gen_sign(sign_str=sign_str)

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
