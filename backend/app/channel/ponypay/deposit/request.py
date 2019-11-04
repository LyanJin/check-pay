import traceback
from decimal import Decimal

import requests
import json

from flask import current_app

from app.channel.deposit_base import DepositRequestBase
from app.enums.third_enum import SdkRenderType
from app.libs.datetime_kit import DateTimeKit
from app.libs.string_kit import RandomString

#
# def third_pay(order, form):
#     current_channel = form.channel_id.data
#     channel_id = current_channel.value
#     channel_conf = current_channel.conf
#
#     request_fields = ['pay_type', 'mch_id', 'order_id', 'channel_id', 'pay_amount', 'name', 'explain', 'remark',
#                       'result_url', 'notify_url', 'client_ip', 'bank_cardtype', 'bank_code', 'is_qrimg', 'is_sdk',
#                       'ts', 'sign', 'ext']
#
#     request_fields = sorted(request_fields, key=str.lower)
#
#     order_dict = {}
#     for field in request_fields:
#         # 本次请求使用的支付方式
#         if field in ['channel_id']:
#             order_dict[field] = 76
#         # 支付通道分配给我方的账户id
#         elif field in ['mch_id']:
#             order_dict[field] = channel_id
#         # 支付类型固定为2，标记第三方支付
#         elif field in ['pay_type']:
#             order_dict[field] = 2
#         # 我方的订单号
#         elif field in ["order_id"]:
#             print("**************order_id***********", order.sys_tx_id)
#             order_dict[field] = order.sys_tx_id
#         # 支付总金额
#         elif field in ["pay_amount"]:
#             if isinstance(order.amount, Decimal):
#                 order_dict[field] = order.amount.quantize(Decimal("0.00"))
#             else:
#                 order_dict[field] = Decimal(str(order.amount)).quantize(Decimal("0.00"))
#         # 商品名
#         elif field in ["name"]:
#             order_dict[field] = "SHANGPINMINGCHENG"
#         # 商品描述 可不填
#         elif field in ["explain"]:
#             order_dict[field] = "SHANGPINMIAOSHU"
#         # 订单附加说明 可不填
#         elif field in ["remark"]:
#             order_dict[field] = "SHANGPINBEIZHU"
#         # 同步跳转地址 在wap类型的支付通道中有效  可不填
#         elif field in ["result_url"]:
#             order_dict[field] = "result_url"
#         # notify_url 接受订单通知的url
#         elif field in ["notify_url"]:
#             order_dict[field] = channel_conf['callback_url']
#         # client_ip 客户端用户ip
#         elif field in ["client_ip"]:
#             order_dict[field] = form.client_ip.data
#         # 仅在二维码类型的支付通道中有效
#         elif field in ["is_qrimg"]:
#             order_dict[field] = False
#         # 是否直接拉起支付
#         elif field in ["is_sdk"]:
#             order_dict[field] = True
#         # ts 时间戳
#         elif field in ["ts"]:
#             order_dict[field] = DateTimeKit.get_cur_timestamp()
#         # ext 附加信息
#         elif field in ["ext"]:
#             order_dict[field] = "FUJIAXINXI"
#
#     sign_str = "&".join([
#         "{}={}".format(field, order_dict[field])
#         for field in request_fields
#         if order_dict.get(field, None)])
#
#     sign_str += "&key=%s" % (channel_conf['secret_key'])
#     sign = RandomString.gen_md5_string(sign_str.encode("utf-8")).upper()
#     print("***************sign", sign, 'FFCCB9A82C56901771A938019EEAFD84')
#     order_dict['sign'] = sign
#
#     resp = requests.post(url=channel_conf['post_url'], data=order_dict)
#     print(resp.text)
#     print("****************************")
#     print(resp.content)
#     print("*****************************")
#     print(resp.json)
#     print("******************************")
#     print(resp.reason)
#     print(dir(resp))
#     if resp.json == 0:
#         sign = resp.json['sign']
#         code_url = resp.json['code_url']
#         code_img_url = resp.json['code_img_url']
#         pay_type = resp.json['pay_type']
#         mch_id = resp.json['mch_id']
#         order_id = resp.json['order_id']
#         channel_id = resp.json['channel_id']
#         pay_amount = resp.json['pay_amount']
#         real_amount = resp.json['real_amount']
#         status = resp.json['status']
#         order_no = resp.json['order_no']
#         finish_time = resp.json['finish_time']
#         ext = resp.json['ext']
#     # return code_url


class DepositRequest(DepositRequestBase):

    def launch_pay(self, order, params: dict):
        """
        立马支付，充值请求
        :param order:
        :param params:
        :return:
        """
        current_channel = params['channel_enum']
        channel_conf = current_channel.conf

        request_fields = ["merchant_id", "orderid", "paytype", "notifyurl", "callbackurl", "userip", "money", "sign"]
        request_dict = {}
        for field in request_fields:
            # 商户号 平台分配 必填
            if field in ["merchant_id"]:
                request_dict[field] = channel_conf['mch_id']
            # 订单号 唯一, 字符长度20 必填
            elif field in ["orderid"]:
                print("order.sys_tx_id:>>>>>>>>>>>>>>>>", order.sys_tx_id, order.amount)
                request_dict[field] = order.sys_tx_id
            # 支付方式  ZFBH5 必填
            elif field in ["paytype"]:
                request_dict[field] = channel_conf['third_paytype']
            # 服务端通知  服务端返回地址.（POST返回数据）必填
            elif field in ["notifyurl"]:
                request_dict[field] = channel_conf["callback_url"]
            # 页面跳转通知 页面跳转返回地址（POST返回数据） 必填
            elif field in ["callbackurl"]:
                request_dict[field] = channel_conf['callback_url']
            # 客户IP地址 必填 不参与签名 （微信必须使用）
            elif field in ["userip"]:
                request_dict[field] = params['client_ip']
            # 订单金额 必填 商品金额
            elif field in ["money"]:
                if isinstance(order.amount, Decimal):
                    request_dict[field] = order.amount.quantize(Decimal("0.00"))
                else:
                    request_dict[field] = Decimal(str(order.amount)).quantize(Decimal("0.00"))

        sign_str = "".join(
            ["{}".format(request_dict[item]) for item in request_fields if item not in ["userip", "sign"]])
        sign_str += "{}".format(channel_conf['secret_key'])
        request_dict['sign'] = RandomString.gen_md5_string(sign_str.encode("gb2312")).lower()

        headers = {}
        user_agent = params['user_agent']
        if user_agent:
            headers.update({'User-Agent': user_agent})

        try:
            current_app.logger.info('ponypay deposit, url: %s, headers: %s, data: %s',
                                     channel_conf['post_url'], headers, request_dict)

            resp = requests.post(url=channel_conf['post_url'], data=request_dict, headers=headers)

            current_app.logger.info('ponypay deposit, status_code: %s, content: %s', resp.status_code, resp.text)
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
            status = resp_data['status']
            if status == "0":
                msg = resp_data['message']
                code = -1
            elif status == "1":
                if not resp_data["data"]["url"].startswith("http"):
                    msg = resp_data["data"]["url"]
                    code = -2
                # 正确的数据
                render_content = resp_data["data"]["url"]
        else:
            code = resp.status_code
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
