import json
import os
import traceback

import requests
from flask import current_app

from app.channel.bestpay.deposit.callback import CallbackBestPay
from app.channel.deposit_base import DepositRequestBase
from app.enums.third_enum import SdkRenderType
from app.enums.trade import PayMethodEnum
from app.libs.datetime_kit import DateTimeKit


class DepositRequest(DepositRequestBase):

    def gen_url(self):
        host = self.third_config['post_bank_info_url']
        return host

    def parse_response(self, resp, order, params: dict, render_type):
        if resp.status_code != 200:
            return dict(
                code=-100,
                msg='http请求失败，状态: %s' % resp.status_code,
                data=dict(),
            )

        data = resp.json()

        if data['success'] == "true":
            data = data['data']
            d1 = data[0]
            return dict(
                code=0,
                msg='ok',
                # 商户订单号
                data=dict(
                    render_type=render_type,  # 类型
                    render_content=json.dumps(dict(tx_id=order.order_id,
                                                   CardName=d1['CardName'],
                                                   CardNumber=d1['CardNumber'],
                                                   BankName=d1['BankName'],
                                                   DepositStart=d1['DepositStart'],
                                                   DepositEnd=d1['DepositEnd'],
                                                   start_time=DateTimeKit.get_cur_timestamp(),
                                                   channel_id=self.channel_enum.value,
                                                   amount=str(order.amount)))
                ),
            )
        else:
            return dict(
                code=-999,
                msg='state: {}, error_message:{}'.format(data.get('success', 'False'),
                                                         data.get('error_message', 'False')),
                data=dict()
            )

    def construct_request(self, order, params: dict):
        pay_params = {
            PayMethodEnum.BANK_TO_BANK: dict(defaultbank="BANK_TO_BANK", render_type=SdkRenderType.TRANSFER),
            PayMethodEnum.ZHIFUBAO_TO_BANK: dict(defaultbank="BANK_TO_BANK", render_type=SdkRenderType.TRANSFER),
            PayMethodEnum.WEIXIN_TO_BANK: dict(defaultbank="WEIXIN_TO_BANK", render_type=SdkRenderType.TRANSFER),
        }

        payment_method = self.channel_enum.conf['payment_method']
        request_fields = ['method', 'company_key', 'data_sign']

        request_body = {}
        for field in request_fields:
            if field == "method":
                request_body[field] = "get_banklist"
            elif field == "company_key":
                request_body[field] = self.third_config['mch_id']
        render_type = pay_params[payment_method]['render_type']
        print("secret_key:%s" % self.third_config['secret_key'])
        return request_body, '', render_type

    def launch_pay(self, order, params: dict):

        url = self.gen_url()

        request_body, sign_str, render_type = self.construct_request(order, params)

        sign = CallbackBestPay.gen_sign(sign_str=sign_str)
        request_body['data_sign'] = sign
        headers = {"Content-Type": "application/json;charset=UTF-8"}
        try:
            current_app.logger.info('BestPay Select Bank, url: %s, data: %s', url, request_body)
            resp = requests.post(url=url, json=request_body, headers=headers)
            current_app.logger.info('BestPay Select Bank response, status_code: %s, content: %s', resp.status_code,
                                    resp.text)
        except Exception as e:
            current_app.logger.fatal(traceback.format_exc())
            return dict(
                code=-100,
                msg="http请求失败",
                data=dict(),
            )

        return self.parse_response(resp, order, params, render_type)
