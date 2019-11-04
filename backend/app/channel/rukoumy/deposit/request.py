import json
import os
import traceback
import requests
from flask import current_app

from app.channel.deposit_base import DepositRequestBase
from app.channel.rukoumy.deposit.callback import CallbackRuKouMy
from app.channel.vpay.deposit.callback import CallbackVpay
from app.enums.third_enum import SdkRenderType
from app.enums.trade import PayMethodEnum
from app.libs.balance_kit import BalanceKit
from app.libs.datetime_kit import DateTimeKit


class DepositRequest(DepositRequestBase):

    def gen_url(self):
        host = self.third_config['post_url'].strip('/')
        path = self.third_config['deposit_path'].strip('/')
        return os.path.join(host, path)

    def construct_request(self, order, params: dict):
        pay_params = {
            PayMethodEnum.ZHIFUBAO_H5: dict(channel=7, render_type=SdkRenderType.QR_CODE),
            PayMethodEnum.WEIXIN_H5: dict(channel=1, render_type=SdkRenderType.QR_CODE)
        }

        payment_method = self.channel_enum.conf['payment_method']
        request_fields = ['pay_type', 'mch_id', 'order_id', 'channel_id', 'pay_amount', 'name',
                          'explain', 'remark', 'result_url', 'notify_url', 'client_ip',
                          'bank_cardtype', 'bank_code', 'is_qrimg', 'is_sdk', 'ts', 'sign', 'ext']
        sorted_params = sorted(request_fields)

        request_body = {}

        for field in request_fields:
            if field == "pay_type":
                request_body[field] = 2
            elif field == "mch_id":
                request_body[field] = int(self.third_config['mch_id'])
            elif field == "order_id":
                request_body[field] = order.sys_tx_id
            elif field == "channel_id":
                request_body[field] = pay_params[payment_method]['channel']
            elif field == "pay_amount":
                request_body[field] = str(BalanceKit.round_4down_5up(order.amount))
            elif field == "name":
                request_body[field] = "mch name"
            elif field == "explain":
                request_body[field] = "explain text"
            elif field == "remark":
                request_body[field] = "remark message"
            elif field == "result_url":
                request_body[field] = self.third_config['return_url']
            elif field == "notify_url":
                request_body[field] = self.third_config['callback_url']
            elif field == "client_ip":
                request_body[field] = params['client_ip']
            elif field == 'is_qrimg':
                request_body[field] = 0
            elif field == 'is_sdk':
                request_body[field] = 1
            elif field == 'ts':
                request_body[field] = DateTimeKit.get_cur_timestamp()
            elif field == 'ext':
                request_body[field] = "ext message"

        sign_str = "&".join(["{}={}".format(k, request_body[k]) for k in sorted_params if
                             request_body.get(k, False) or k in ["is_qrimg", "is_sdk"]])
        # sign_str += self.third_config['secret_key']

        print("sign string: ", sign_str)
        print("request body: ", request_body)

        render_type = pay_params[payment_method]['render_type']

        return request_body, sign_str, render_type

    def launch_pay(self, order, params: dict):

        url = self.gen_url()

        request_body, sign_str, render_type = self.construct_request(order, params)

        sign = CallbackRuKouMy.gen_sign(sign_str=sign_str)

        request_body["sign"] = sign

        headers = {
            'Content-Type': 'application/json;charset=UTF-8'
        }

        code = 0
        msg = ''
        try:
            current_app.logger.info(
                'Taiysg deposit request url: {}, data: {}, headers:{}'.format(url, request_body, headers))
            kwargs = dict(headers=headers, verify=False)
            resp = requests.post(url=url, json=request_body, **kwargs)
            current_app.logger.info('Taiysg deposit response, status_code: %s, content: %s', resp.status_code,
                                    resp.text)
        except Exception as e:
            current_app.logger.fatal(traceback.format_exc())
            code = -1
            msg = "http请求异常"

            return dict(
                code=code,  # 错误码，code=0是没有错误
                msg=msg,  # 当code不等于0时，填写错误提示信息
                data=dict(
                    render_type=render_type,  # 类型
                    render_content=str(e),  # 内容
                ),
            )
            # 统一返回值

        render_content = ""

        if resp.status_code != 200:
            code = int(resp.status_code)
            msg = resp.text
        else:
            data = json.loads(resp.text)

            if data['code'] == 0:
                render_content = data['code_url']
            else:
                msg = data['msg']
                code = data['code']

        return dict(
            code=code,  # 错误码，code=0是没有错误
            msg=msg,  # 当code不等于0时，填写错误提示信息
            data=dict(
                render_type=render_type,  # 类型
                render_content=render_content,  # 内容
            ),
        )
