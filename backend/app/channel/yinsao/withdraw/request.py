import traceback
from decimal import Decimal

import requests
from flask import current_app

from app.channel.withdraw_base import ProxyPayRequest
from app.channel.yinsao.deposit.callback import CallbackYinSao
from app.channel.yinsao.withdraw.callback import WithdrawCallbackYinSao
from app.libs.datetime_kit import DateTimeKit

System_Third_party = {
    "ABC": "中国农业银行",
    "BOC": "中国银行",
    "ICBC": "中国工商银行",
    "CCB": "中国建设银行",
    "PSBC": "中国邮政储蓄银行",
    "CMB": "招商银行",
    "SPDB": "上海浦东发展银行",
    "CMBC": "中国民生银行",
    "SPABANK": "平安银行",
    "CITIC": "中信银行",
    "HXBANK": "华夏银行",
    "CEB": "中国光大银行",
    "CIB": "兴业银行",
    "GDB": "广发银行",
    "COMM": "交通银行"
}


class WithdrawRequest(ProxyPayRequest):

    def parse_response(self, resp):
        if resp.status_code != 200:
            return dict(
                code=-100,
                msg='http请求失败，状态: %s' % resp.status_code,
                data=dict(),
            )
        data = resp.json()
        if data.get('respCode', False) == '0000':
            return dict(
                code=0,
                msg='ok',
                # 商户订单号
                data=dict(tx_id=data['orderNo']),
            )
        else:
            return dict(
                code=-999,
                msg='respCode: {}, respDesc:{}'.format(data.get('respCode', 'False'), data.get('respDesc', 'False')),
                data=dict()
            )

    def construct_request(self, params_dict: dict):
        tx_id = params_dict['tx_id']
        amount = params_dict['amount']
        bank_name = params_dict['bank_name']
        bank_account = params_dict['bank_account']
        bank_number = params_dict['bank_number']
        bank_address = params_dict['bank_address']
        bank_code = params_dict['bank_code']
        request_fields = ['version', 'merNo', 'orderNo', 'orderDate', 'transId', 'transAmt', 'notifyUrl',
                          'customerName',
                          'acctNo', 'bankCode', 'accBankName', 'note']
        fields = sorted(request_fields)
        request_dict = {}
        for field in fields:
            if field == 'version':
                request_dict[field] = 'V1.1'
            elif field == 'merNo':
                request_dict[field] = self.third_config['mch_id']
            elif field == 'orderNo':
                request_dict[field] = tx_id
            elif field == 'orderDate':
                request_dict[field] = DateTimeKit.get_cur_timestamp()
            # 交易类型 固定值
            elif field == 'transId':
                request_dict[field] = '0101'
            # 交易金额 单位 分
            elif field == 'transAmt':
                if isinstance(amount, Decimal):
                    request_dict[field] = int(amount * Decimal('100'))
                else:
                    request_dict[field] = int(Decimal(str(amount)) * Decimal("100"))
            # 后台回调地址
            elif field == 'notifyUrl':
                request_dict[field] = self.third_config['callback_url']
            # 开户人名称
            elif field == 'customerName':
                request_dict[field] = bank_account
            elif field == 'acctNo':
                request_dict[field] = bank_number
            elif field == 'bankCode':
                request_dict[field] = System_Third_party[bank_code] if System_Third_party.get(bank_code,
                                                                                              False) else bank_name
            elif field == 'accBankName':
                request_dict[field] = bank_address
            elif field == 'note':
                request_dict[field] = 'node'

        request_body_str = "&".join(["{}={}".format(k, v) for k, v in request_dict.items()])
        sign = WithdrawCallbackYinSao.generate_sign(request_fields_str=request_body_str, third_config=self.third_config)
        request_dict['signature'] = sign
        return request_dict

    def launch_pay(self, params_dict: dict):
        """
        发起支付
        :return:
        """
        body = self.construct_request(params_dict)

        url = self.gen_url()
        try:
            current_app.logger.info('yinsao withdraw, url: %s, data: %s', url, body)
            resp = requests.post(url=url, data=body)
            current_app.logger.info('yinsao withdraw, status_code: %s, content: %s', resp.status_code, resp.text)
        except Exception as e:
            current_app.logger.fatal(traceback.format_exc())
            return dict(
                code=-100,
                msg="http请求失败",
                data=dict(),
            )

        return self.parse_response(resp)
