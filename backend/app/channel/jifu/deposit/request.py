"""
签名算法
签名生成的通用步骤如下：
第一步，设所有接收到的数据为集合M，将集合M内非空参数值的参数按照参数名ASCII码从小到大排序（字典序），使用URL键值对的格式（即key1=value1&key2=value2…）拼接成字符串stringA。
特别注意以下重要规则：
◆ 参数名ASCII码从小到大排序（字典序）；
◆ 如果参数的值为空不参与签名；
◆ 参数名区分大小写；
◆ 验证调用返回时，传送的sign参数不参与签名，将生成的签名与该sign值作校验。
◆ 接口可能增加字段，验证签名时必须支持增加的扩展字段
第二步，在stringA最后拼接上key得到stringSignTemp字符串，并对stringSignTemp进行MD5运算，再将得到的字符串所有字符转换为大写，得到sign值signValue。
举例：
假设收到的参数如下：
id： wxd930ea5d5a258f4f
money：  10000100
remark： 1000
nonce_str ：ewfgrweagerw
sign：   ibuaiVcKdpRxkhJA

第一步：对参数按照key=value的格式，并按照参数名ASCII字典序排序如下：
stringA="id=wxd930ea5d5a258f4f&money=10000100&nonce_str=ewfgrweagerw&remark=1000";
第二步：拼接API密钥：
stringSignTemp=stringA+"&key=192006250b4c09247ec02edce69f6a2d" //注：key为商户平台设置的专用验签密钥key
sign=MD5(stringSignTemp).toUpperCase()="9A0A8659F005D6984697E2CA0A9CF3B7" //注：MD5签名方式

最终将返回的参数中的sign与生成的sign做对比。

"""
import traceback

import requests

from flask import current_app

from app.channel.deposit_base import DepositRequestBase
from app.enums.third_enum import SdkRenderType
from app.libs.string_kit import RandomString


class DepositRequest(DepositRequestBase):

    def launch_pay(self, order, params: dict):
        """
        极付，充值请求
        :param order:
        :param params:
        :return:
        """
        post_data = self.construct_request(order, params)
        headers = self.construct_headers(params)
        post_url = self.gen_url()

        try:
            current_app.logger.info('jifu deposit, sys_tx_id: %s, url: %s, headers: %s, data: %s',
                                    order.sys_tx_id, post_url, headers, post_data)
            rsp = requests.post(post_url, json=post_data, headers=headers)
            current_app.logger.info('jifu deposit, sys_tx_id: %s, status_code: %s, content: %s',
                                    order.sys_tx_id, rsp.status_code, rsp.text)
        except:
            current_app.logger.fatal(traceback.format_exc())
            return dict(
                code=-1,
                msg="http请求异常",
                data=dict(),
            )

        return self.parse_response(rsp)

    @classmethod
    def join_sign_str(cls, params: dict):
        keys = sorted(list(params.keys()))
        return '&'.join(["=".join(map(str, [k, params[k]])) for k in keys if params[k]])

    def generate_sign(self, params: dict):
        """
        生成签名
        :param params:
        :return:
        """
        raw_str = self.join_sign_str(params)
        raw_str += '&key=' + self.get_secret_key()
        # current_app.logger.info('raw_str: %s', raw_str)
        # current_app.logger.info('raw_str utf8: %s', raw_str.encode('utf8'))
        sign = RandomString.gen_md5_string(raw_str.encode('utf8')).upper()
        return sign

    def construct_request(self, order, params: dict):
        """
        填写请求参数
        :param order:
        :param params:
        :return:
        """
        request_data = dict(
            appId=self.channel_conf.app_id,
            nonce_str=RandomString.gen_random_str(16),
            pay_type=self.channel_conf.third_paytype,
            callback_url=self.channel_conf.callback_url,
            money_amount=str(order.amount),
            # 可以通过remark来传自己的订单号，回调的时候传回
            remark=order.sys_tx_id,
        )

        sign = self.generate_sign(request_data)
        request_data['sign'] = sign

        return request_data

    def parse_response(self, rsp):
        """
        解析响应
        {
            "result": 1,
            "message": "success",
            "data": {
                "order": {
                    "appid": "1asdssfasfasdf",
                    "pay_type": "2",
                    "Callback_url": "www.baidu.com", #回调地址
                    "money_amount": "500", #法币金额
                    "code": "96f8f7a1077c8147", #订单唯一code值
                    "usdt": 71.32667, #usdt金额
                    "orderid": 37844, #订单id
                    "addtime": 1565257758, #订单创建时间
                    "sendout": 2,
                    "remark": "自动订单备注",
                    "id": 31418,
                    "jump_url": "http:///www.cheapusdt.com/pages/maiInfo.html" #订单创建成功后，跳转的地址
                }
            },
            "success_code": "0"
        }

        * 将 code 放入数据库中，等回调时拿来比对
        * 将jump_url 和code组成支付二维码网址返给用户
        * 如： http://www.cheapusdt.com/pages/maiInfo.html?id=9018cae93442157c

        失败响应
        参数不正确响应
        {
            "result": 0,
            "message": "付款方式参数不能为空"
        }
        功能性响应
        {
            "result": 0,
            "message": "商户已被关闭创建订单功能",
            "error_code": "0"
        }

        :param rsp:
        :return:
        """
        render_content = None
        channel_tx_id = None
        code = 0
        msg = None

        if rsp.status_code == 200:
            json_data = rsp.json()
            if json_data['result'] == 1 and json_data['success_code'] == "0":
                # 通道侧强烈建议保留code，后续订单查询可以提供code去查
                channel_tx_id = json_data['data']['order']['code']
                render_content = json_data['data']['order']['jump_url'] + "?id=" + channel_tx_id
            else:
                code = -98
                msg = json_data['message']
        else:
            code = -99
            msg = 'HTTP响应状态码非200: %s' % rsp.status_code

        # 统一返回值
        return dict(
            code=code,  # 错误码，code=0是没有错误
            msg=msg,    # 当code不等于0时，填写错误提示信息
            data=dict(
                render_type=SdkRenderType.URL,  # 类型
                render_content=render_content,  # 内容
                channel_tx_id=channel_tx_id     # 通道订单号
            ),
        )
