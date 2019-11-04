import json
import os
import traceback
import requests
from flask import current_app

from app.channel.deposit_base import DepositRequestBase
from app.channel.vpay.deposit.callback import CallbackVpay
from app.libs.datetime_kit import DateTimeKit


class DepositRequest(DepositRequestBase):

    def gen_url(self, order):
        host = self.third_config['post_url'].strip('/')
        path = self.third_config['deposit_path'].strip('/')
        return os.path.join(host, path)

    def construct_request(self, order, params: dict):
        request_fields = ['amount', 'api_version', 'channel', 'isSign', 'merchant_id', 'merchant_order_no',
                          'notify_url',
                          'timestamp', 'sign']
        sorted_params = sorted(request_fields)

        request_body = {}

        for field in request_fields:
            if field == "api_version":
                request_body[field] = "1.1"
            elif field == "channel":
                request_body[field] = self.channel_enum.conf['request_config'][field]
            elif field == "isSign":
                request_body[field] = "abc"
            elif field == "merchant_id":
                request_body[field] = self.third_config['mch_id']
            elif field == "merchant_order_no":
                request_body[field] = order.sys_tx_id
            elif field == "notify_url":
                request_body[field] = self.third_config["callback_url"]
            elif field == "timestamp":
                request_body[field] = DateTimeKit.get_cur_timestamp()
            elif field == "amount":
                request_body[field] = float(order.amount)

        sign_str = "&".join(["{}={}".format(k, request_body[k]) for k in sorted_params if request_body.get(k, False)])
        # sign_str += self.third_config['secret_key']

        print("sign string: ", sign_str)
        print("request body: ", request_body)

        return request_body, sign_str

    def launch_pay(self, order, params: dict):

        url = self.gen_url(order)

        request_body, sign_str = self.construct_request(order, params)

        sign = CallbackVpay.gen_sign(sign_str=sign_str)

        request_body["sign"] = sign

        headers = {
            'Content-Type': 'application/json;charset=UTF-8'
        }

        code = 0
        msg = ''
        render_content = ''

        try:
            current_app.logger.info(
                'Vpay deposit request url: {}, data: {}, headers:{}'.format(url, request_body, headers))
            kwargs = dict(headers=headers, verify=False)
            resp = requests.post(url=url, json=request_body, **kwargs)
            current_app.logger.info('Vpay deposit response, status_code: %s, content: %s', resp.status_code,
                                    resp.text)
        except Exception as e:
            current_app.logger.error('An error occurred.', exc_info=True)
            code = -1
            msg = "http请求异常"
        else:
            if resp.status_code != 200:
                code = int(resp.status_code)
                msg = resp.text
            else:
                # if resp.respCode [S0001, F9999]  respMessage [请求已成功执行, 服务器系统繁忙]
                resp_data = json.loads(resp.text)
                render_content = resp.text
                if resp_data.get('code', "") != 200:
                    code = resp_data.get("code", "") if resp_data.get("code", "") else resp_data.get("status")
                    msg = resp_data.get("msg", "") if resp_data.get("msg", "") else resp_data.get("message")
                else:
                    render_content = resp_data['data']['payUrl']

        return dict(
            code=code,  # 错误码，code=0是没有错误
            msg=msg,  # 当code不等于0时，填写错误提示信息
            data=dict(
                render_type=self.channel_enum.conf['render_type'],  # 类型
                render_content=render_content,  # 内容
            ),
        )
