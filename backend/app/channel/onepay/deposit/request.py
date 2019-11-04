import os
import traceback

import requests
from flask import current_app
from decimal import Decimal

from app.channel.deposit_base import DepositRequestBase
from app.channel.onepay.deposit.callback import CallbackOnePay
from app.enums.third_enum import SdkRenderType
from app.enums.trade import PayMethodEnum


class RequestOnePay(DepositRequestBase):
    """
        易付充值
    """

    def gen_url(self):
        host = self.third_config['post_url'].strip('/')
        path = self.third_config['deposit_path'].strip('/')
        return os.path.join(host, path)

    def construct_request(self, order, params: dict):
        request_fields = ['version', 'inputCharset', 'signType', 'returnUrl', 'notifyUrl', 'deviceType', 'payType',
                          'merchantId', 'merchantTradeId', 'currency', 'amountFee', 'goodsTitle', 'issuingBank']

        device_type = 'H5'
        pay_type = 'NC'
        if pay_type == 'EC':
            device_type = 'WEB'
            request_fields.append('subIssuingBank')
        elif pay_type == 'NC':
            # device_type in ['H5', 'WEB']
            request_fields.append('cardType')
        elif pay_type == 'CARDBANK':
            device_type = 'WEB'
            request_fields += ['cardType', 'paymentCard', 'userName']

        no_need_sign_fields = ['paymentCard', 'userName', 'signType', 'sign']

        sorted_request = sorted(request_fields)
        request_dict = {}
        for item in sorted_request:
            if item == 'version':
                request_dict[item] = '1.0'
            elif item == 'inputCharset':
                request_dict[item] = 'UTF-8'
            elif item == 'signType':
                request_dict[item] = 'RSA'
            elif item == 'payIp':
                request_dict[item] = '127.0.0.1'
            elif item == 'returnUrl':
                request_dict[item] = self.third_config['result_url']
            elif item == 'notifyUrl':
                request_dict[item] = self.third_config['callback_url']
            elif item == 'deviceType':
                request_dict[item] = device_type
            elif item == 'payType':
                request_dict[item] = pay_type
            elif item == 'merchantId':
                request_dict[item] = self.third_config['mch_id']
            elif item == 'merchantTradeId':
                request_dict[item] = order.sys_tx_id
            elif item == 'currency':
                request_dict[item] = 'CNY'
            elif item == 'amountFee':
                amount = str(order.amount)
                if amount.find('.') <= -1:
                    amount += '.00'
                request_dict[item] = amount
            elif item == 'goodsTitle':
                request_dict[item] = 'goods title'
            elif item == 'issuingBank':
                request_dict[item] = 'UNIONPAY'
            elif item == 'subIssuingBank':
                request_dict[item] = ''
            elif item == 'cardType':
                request_dict[item] = 'D'
            elif item == 'paymentCard':
                request_dict[item] = "6214982318340483"
            elif item == 'userName':
                request_dict[item] = '张三'
        request_str = '&'.join(["{}={}".format(item, request_dict[item]) for item in sorted_request if
                                request_dict.get(item, False) and item not in no_need_sign_fields])

        return request_dict, request_str, pay_type

    def launch_pay(self, order, params: dict):
        data_dict, request_str, pay_type = self.construct_request(order, params)
        sign = CallbackOnePay.gen_sign(request_str)
        data_dict['sign'] = sign
        url = self.gen_url()
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        code = 0
        msg = ''
        try:
            current_app.logger.info(
                'one pay deposit request url: {}, data: {}, headers:{}'.format(url, data_dict, headers))
            kwargs = dict(headers=headers, verify=False)
            resp = requests.post(url=url, data=data_dict, **kwargs)
            current_app.logger.info('one pay deposit response, status_code: %s, content: %s', resp.status_code,
                                     resp.text)
        except Exception as e:
            current_app.logger.fatal(traceback.format_exc())
            code = -1
            msg = "http请求异常"
            # 统一返回值

        if resp.status_code != 200:
            code = int(resp.status_code)
            msg = resp.text

        return dict(
            code=code,  # 错误码，code=0是没有错误
            msg=msg,  # 当code不等于0时，填写错误提示信息
            data=dict(
                render_type=SdkRenderType.HTML,  # 类型
                render_content=resp.text,  # 内容
            ),
        )


class RequestQROnePay(DepositRequestBase):

    def gen_url(self):
        host = self.third_config['post_url'].strip('/')
        path = self.third_config['deposit_path'].strip('/')
        return os.path.join(host, path)

    def construct_request(self, order, params: dict):
        request_fields = ['app_id', 'currency', 'amount', 'order_no', 'payment_channel']

        payment_dict = {
            PayMethodEnum.ZHIFUBAO_SAOMA: 'ALIPAY',
            PayMethodEnum.WEIXIN_SAOMA: 'WECHAT',
            PayMethodEnum.YUNSHANFU: 'UNIONPAY',
        }

        sorted_request = sorted(request_fields)
        request_dict = {}
        for item in sorted_request:
            if item == 'payment_channel':
                request_dict[item] = payment_dict[self.channel_enum.conf['payment_method']]
            elif item == 'app_id':
                request_dict[item] = self.third_config['mch_id']
            elif item == 'order_no':
                request_dict[item] = order.sys_tx_id
            elif item == 'currency':
                request_dict[item] = 'CNY'
            elif item == 'amount':
                amount = str(order.amount)
                if amount.find('.') > -1:
                    amount = amount.split('.')[0]
                request_dict[item] = int(amount)

        return request_dict

    def launch_pay(self, order, params: dict):
        data_dict = self.construct_request(order, params)
        url = self.gen_url()
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        code = 0
        msg = None
        render_content = ''

        try:
            current_app.logger.info(
                'one pay QR deposit request url: {}, data: {}, headers:{}'.format(url, data_dict, headers))
            kwargs = dict(headers=headers, verify=False)
            resp = requests.post(url=url, data=data_dict, **kwargs)
            current_app.logger.info('one pay QR deposit response, status_code: %s, content: %s', resp.status_code,
                                     resp.text)
        except Exception as e:
            current_app.logger.fatal(traceback.format_exc())
            code = -1
            msg = "http请求异常"

        else:

            if resp.status_code != 200:
                code = int(resp.status_code)
                msg = resp.text

            json_data = resp.json()
            data = json_data.get('data', False)
            flag = json_data.get('flag', False)

            if not data or flag != 'SUCCESS':
                code = -99
                msg = json_data.get('errorMsg') or 'errorMsg'
            elif flag == 'SUCCESS' and not data['qrUrl']:
                code = -99
                msg = data['message']
            else:
                render_content = data['qrUrl']

        return dict(
            code=code,  # 错误码，code=0是没有错误
            msg=msg,  # 当code不等于0时，填写错误提示信息
            data=dict(
                render_type=SdkRenderType.QR_CODE,  # 类型
                render_content=render_content,  # 内容
            ),
        )
