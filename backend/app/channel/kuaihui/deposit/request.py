import traceback
from decimal import Decimal

import requests
import json
import time

from flask import current_app

from app.channel.deposit_base import DepositRequestBase
from app.enums.third_enum import SdkRenderType
from app.libs.datetime_kit import DateTimeKit
from app.libs.string_kit import RandomString
from app.libs.kuaihui.sdk import sig


class DepositRequest(DepositRequestBase):

    def launch_pay(self, order, params: dict):
        """
        快汇支付，充值请求
        :param order:
        :param params:
        :return:
        """
        current_channel = params['channel_enum']
        channel_conf = current_channel.conf

        # 调用sdk
        s = sig.Sig(channel_conf['secret_key'])

        # 调用收款订单创建api
        param = {
            "custid": channel_conf['custid'],
            "client_ordid": order.sys_tx_id,
            "accountname": "张三",
            "accountid": "123456789",
            "bankcode": "bank",
            "channel": "bank",
            "amount": Decimal(str(order.amount)).quantize(Decimal("0.00")),
            "bgreturl": channel_conf["callback_url"],
            "timestamp": str(int(time.time()))
        }

        param["sig"] = s.create("POST", "/deposit_requests", param)

        url = '{apiUrl}/deposit_requests'.format(apiUrl=channel_conf['apiUrl'])

        try:
            # 记录请求的数据
            current_app.logger.info('kuaihui deposit, url: %s, data: %s', url, param)

            resp = requests.post(url, param)

            # 记录返回结果
            current_app.logger.info('kuaihui deposit, status_code: %s, content: %s', resp.status_code, resp.text)
        except:
            current_app.logger.fatal(traceback.format_exc())
            return dict(
                code=-1,
                msg="http请求异常",
                data=dict(),
            )

        code = 0
        msg = ""
        render_content = None

        if resp.status_code == 200:
            resp_data = resp.json()
            status_code = resp_data['status_code']
            # print(status_code)
            if status_code == 200:
                # 正确的数据
                render_content = resp_data["data"]["ckcurl"]
            else:
                code = -1
                msg = resp_data['message']
        else:
            code = -2
            msg = resp.text

        # 统一返回值
        return dict(
            code=code,             # 错误码，code=0是没有错误
            msg=msg,             # 当code不等于0时，填写错误提示信息
            data=dict(
                render_type=SdkRenderType.URL,      # 类型
                render_content=render_content,               # 内容
            ),
        )



if __name__ == '__main__':
    """    
    """
    DR = DepositRequest()
    # flag, msg = DR.launch_pay({"sys_tx_id": "13213131", "amount": "18"}, {"channel_id.data":"104"})
    # print(flag)
    # print(msg)
