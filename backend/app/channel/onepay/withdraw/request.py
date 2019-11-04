import traceback
from decimal import Decimal

import requests
from flask import current_app

from app.channel.onepay.withdraw.callback import CallbackOnePay
from app.channel.withdraw_base import ProxyPayRequest
from app.libs.datetime_kit import DateTimeKit, DateTimeFormatEnum


class WithdrawRequest(ProxyPayRequest):

    def parse_response(self, resp):
        if resp.status_code != 200:
            return dict(
                code=-100,
                msg='http请求失败，状态: %s' % resp.status_code,
                data=dict(),
            )
        data = resp.json()
        if data.get('flag', False) == 'SUCCESS':
            return dict(
                code=0,
                msg='ok',
                # 商户订单号
                data=dict(tx_id=data['data']['batchNo']),
            )
        else:
            return dict(
                code=-999,
                msg='errorCode: {}, errorMsg:{}'.format(data.get('errorCode', 'False'), data.get('errorMsg', 'False')),
                data=dict()
            )

    def construct_request(self, params_dict: dict):
        tx_id = params_dict['tx_id']
        amount = Decimal(params_dict['amount'])
        bank_code = params_dict['bank_code']
        bank_account = params_dict['bank_account']
        bank_number = params_dict['bank_number']
        request_fields = ['merchantId', 'batchNo', 'batchRecord', 'currencyCode', 'totalAmount', 'payDate',
                          'isWithdrawNow',
                          'notifyUrl',
                          'signType', 'sign', 'detailList']
        detail_list = ['receiveType', 'accountType', 'serialNo', 'amount', 'bankName', 'bankNo', 'receiveName']
        fields = sorted(request_fields)
        request_dict = {}
        for field in fields:
            if field == 'merchantId':
                request_dict[field] = self.third_config['mch_id']
            elif field == 'batchNo':
                request_dict[field] = tx_id
            elif field == 'batchRecord':
                request_dict[field] = 1
            elif field == 'currencyCode':
                request_dict[field] = 'CNY'
            # 交易类型 固定值
            elif field == 'totalAmount':
                tx_amount = amount
                tx_amount = str(tx_amount)
                if tx_amount.find('.') < 0:
                    tx_amount += '.00'
                request_dict[field] = tx_amount
            # 交易金额 单位 分
            elif field == 'payDate':
                request_dict[field] = DateTimeKit.datetime_to_str(DateTimeKit.get_cur_datetime(),
                                                                  DateTimeFormatEnum.TIGHT_DAY_FORMAT)
            # 后台回调地址
            elif field == 'isWithdrawNow':
                request_dict[field] = '3'
            # 开户人名称
            elif field == 'notifyUrl':
                request_dict[field] = self.third_config['callback_url']
            elif field == 'signType':
                request_dict[field] = 'RSA'
            elif field == 'detailList':
                detail = request_dict.get(field, [])
                detail_dict = {}
                for item in detail_list:
                    if item == 'receiveType':
                        detail_dict[item] = '个人'
                    elif item == 'accountType':
                        detail_dict[item] = '储蓄卡'
                    elif item == 'serialNo':
                        detail_dict[item] = tx_id
                    elif item == 'amount':
                        tx_amount = str(amount)
                        if tx_amount.find('.') < 0:
                            tx_amount += '.00'
                        detail_dict[item] = tx_amount
                    elif item == 'bankName':
                        detail_dict[item] = bank_code
                    elif item == 'bankNo':
                        detail_dict[item] = bank_number
                    elif item == 'receiveName':
                        detail_dict[item] = bank_account
                detail.append(detail_dict)
                request_dict[field] = detail

        no_need_fields = ['detailList', 'signType', 'sign']
        request_body_str = "&".join(["{}={}".format(k, request_dict[k]) for k in fields if
                                     k not in no_need_fields and request_dict.get(k, False)])
        sign = CallbackOnePay.gen_sign(body_str=request_body_str, third_config=self.third_config)
        request_dict['sign'] = sign
        return request_dict

    def launch_pay(self, params_dict: dict):
        """
        发起支付
        :return:
        """
        body = self.construct_request(params_dict)

        url = self.gen_url()
        try:
            headers = {"Content-Type": "application/json"}
            current_app.logger.info('one pay withdraw, url: %s, data: %s', url, body)
            resp = requests.post(url=url, json=body, headers=headers)
            current_app.logger.info('one pay withdraw, status_code: %s, content: %s', resp.status_code, resp.text)
        except Exception as e:
            current_app.logger.fatal(traceback.format_exc())
            return dict(
                code=-100,
                msg="http请求失败",
                data=dict(),
            )
        print(resp.json(), resp.text, resp.content)
        return self.parse_response(resp)
