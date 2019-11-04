import os
import traceback
from decimal import Decimal

import requests
from flask import current_app

from app.channel.deposit_base import DepositRequestBase
from app.channel.yinsao.deposit.callback import CallbackYinSao
from app.enums.third_enum import SdkRenderType
from app.libs.datetime_kit import DateTimeKit


class DepositYinSaoRequest(DepositRequestBase):

    def gen_url(self):
        host = self.third_config['post_url'].strip('/')
        path = self.third_config['deposit_path'].strip('/')
        return os.path.join(host, path)

    def launch_pay(self, order, params: dict):
        """
        银扫支付
        :param order:
        :param params:
        :return:
        """
        current_channel = params['channel_enum']
        channel_conf = current_channel.conf

        request_fields = ['version', 'merNo', 'orderNo', 'orderDate', 'transId', 'transAmt', 'notifyUrl', 'buyerName',
                          'orderName', 'orderDesc']
        fields = sorted(request_fields)
        request_dict = {}
        for field in fields:
            if field == 'version':
                request_dict[field] = 'V1.1'
            elif field == 'merNo':
                request_dict[field] = channel_conf['mch_id']
            elif field == 'orderNo':
                request_dict[field] = order.sys_tx_id
            elif field == 'orderDate':
                request_dict[field] = DateTimeKit.get_cur_timestamp()
            # 交易类型 固定值
            elif field == 'transId':
                request_dict[field] = '0101'
            # 交易金额 单位 分
            elif field == 'transAmt':
                if isinstance(order.amount, Decimal):
                    request_dict[field] = int(order.amount * Decimal('100'))
                else:
                    request_dict[field] = int(Decimal(str(order.amount)) * Decimal("100"))
            # 后台回调地址
            elif field == 'notifyUrl':
                request_dict[field] = channel_conf['callback_url']
            elif field == 'buyerName':
                request_dict[field] = 'buyerName'
            elif field == 'orderName':
                request_dict[field] = 'orderName'
            elif field == 'orderDesc':
                request_dict[field] = 'orderDesc'

        request_body_str = "&".join(["{}={}".format(k, v) for k, v in request_dict.items()])
        sign = CallbackYinSao.generate_sign(request_body_str)
        request_dict['signature'] = sign

        url = self.gen_url()

        code = 0
        msg = ""
        render_content = None

        try:
            current_app.logger.info('yinsao deposit request, url: %s, request_dict: %s', url, request_dict)

            resp = requests.post(url=url, data=request_dict)

            current_app.logger.info('yinsao deposit response, status_code: %s, data: %s', resp.status_code, resp.text)

        except:
            # 网络异常
            current_app.logger.error(traceback.format_exc())
            code = -1
            msg = "http请求异常"

        else:
            # 无异常，正常返回了数据
            if resp.status_code == 200:
                data = resp.json()
                if data:
                    if str(data['respCode']) == "0000":
                        if str(data.get('contentType', '')) == '01' and data.get('busContent', False):
                            redirect_url = data.get('busContent', '')
                            if redirect_url.startswith("https://") or redirect_url.startswith("http://"):
                                render_content = redirect_url
                            else:
                                code = -900
                                msg = 'redirect_url:{}'.format(redirect_url)
                        else:
                            code = -999
                            msg = 'contentType:{}, busContent:{}'.format(data.get('contentType', ''), data.get('respDesc', 'False'))
                    else:
                        code = -2
                        msg = 'respCode:{}, msg:{}'.format(str(data.get('contentType', '')), data.get('respDesc', False))

            else:
                code = int(resp.status_code)
                msg = resp.text

        # 统一返回值
        return dict(
            code=code,  # 错误码，code=0是没有错误
            msg=msg,  # 当code不等于0时，填写错误提示信息
            data=dict(
                render_type=SdkRenderType.QR_CODE,  # 类型
                render_content=render_content,  # 内容
            )
        )
