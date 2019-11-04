"""
立马付接口代付API
"""
import traceback
from urllib.parse import quote

import requests
from flask import current_app

from app.enums.channel import ChannelConfigEnum
from app.libs.string_kit import RandomString
from app.channel.withdraw_base import ProxyPayRequest


class WithdrawRequest(ProxyPayRequest):
    """
    立马付代付请求
    """

    def generate_sign(self, merchant_id, notifyurl, userip, data):
        """
        生成签名
        1、将需要参与签名的字段按一下方式连接（空字符串不参与）:
        key为(商户秘钥)
        string  parastring= merchant_id+ notifyurl+userip+data+key;
        2、MD5方式加密 >小写
        string sign=md5(parastring);
        PS：MD5(“1234567890”)=  e10adc3949ba59abbe56e057f20f883e
        """
        params_string = ''.join([merchant_id, notifyurl, userip, data, self.third_config['secret_key']])
        print('签名前的字符串:')
        print(params_string)
        encode_params = params_string.encode("gb2312")
        return RandomString.gen_md5_string(encode_params).lower()

    def construct_request(self, params_dict: dict):
        """
        组织请求数据
        merchant_id	商户号	是	是	平台分配商户号
        notifyurl	异步通知地址	是	否	商户用来接收通知的地址
        userip	提交地址IP	是	是	提交地址的IP，不可为空。
        data 	付款数据（json）此数据请urlencode	是	否	[{
            "corderid": "12334543",  // 商户代付订单号；
            "money": "405.00",   //代付金额，请加手续费5元，实际到账减5元
            "bankname":"中国工商银行",  //银行名称
            "bankusername": "王大锤",   // 用户在银行的姓名
            "bankcode": "633992923483243247327",  //银行账号
            "bankaddress": "开户行地址"   // 例如：中国银行 XXXX支行
        }，…]

        string url = "http://api.ponypay1.com/payforcustom.aspx";
        string datas = "[{\"corderid\":\"14774939\",\"money\":\"100.00\",\"bankname\":\"中国建设银行\",\"bankusername\":\"陈XX\",\"bankcode\":\"62270XXXX328\",\"bankaddress\":\"建设银行\"}]";
        string key = "DC1zFW2A2ixxxxxxx3W3iUmDPbalg45Xg";
        int merchant_id = 955550;
        string userip = "110.78.222.16";
        string notifyurl = "http://center.xxx.com/notify/withdraw/8720.aspx";
        string ip = Lcb.Ip.GetdotIp();
        string strings = merchant_id + notifyurl + userip + datas + key;
        string signs = MD5(strings);
        string post = "uip="+ip+"&merchant_id="+merchant_id+"&notifyurl="+notifyurl+"&userip="+userip+"&data="+Server.UrlEncode(datas)+"&sign="+signs;
        string s = HttpPost(url,post);
        Response.Write(s);
        """
        merchant_id = self.third_config['mch_id']
        notifyurl = self.third_config['withdraw_cb_url']
        userip = self.third_config['server_ip']
        # merchant_id = "95632"  # self.third_config['mch_id']
        # notifyurl = "http://center.xxx.com/notify/withdraw/8720.aspx"  # self.third_config['withdraw_cb_url']
        # userip = "110.78.222.16"  # self.third_config['server_ip']

        # j_data = json.dumps([dict(
        #     corderid=tx_id,
        #     money=str(amount),
        #     bankname=bank_name,
        #     bankusername=bank_account,
        #     bankcode=bank_number,
        #     bankaddress=bank_address,
        # )], separators=[',', ':'])
        # print(j_data)

        data = '[{"corderid":"%s","money":"%s","bankname":"%s","bankusername":"%s","bankcode":"%s","bankaddress":"%s"}]' % (
            params_dict['tx_id'],
            str(params_dict['amount']),
            params_dict['bank_name'],
            params_dict['bank_account'],
            params_dict['bank_number'],
            params_dict['bank_address'],
        )
        print('data:')
        print(data)

        sign = self.generate_sign(merchant_id, notifyurl, userip, data)
        print('签名:')
        print(sign)

        return dict(
            merchant_id=merchant_id,
            notifyurl=notifyurl,
            userip=userip,
            data=quote(data),
            sign=sign,
        )

    def parse_response(self, rsp):
        """
        解析响应
        status	状态	1：正确; 0：错误，此状态时，message中会有提示信息！
        data	数据	[{"corderid":"xxx","status":"1","message":"错误信息！"},…]
            Status:1 为成功建立订单，
            Status：0 为未建立订单，message为错误信息。
        message	提示信息	 错误提示信息
        data2	交易流水号	 预留
        """
        if rsp.status_code != 200:
            return dict(
                code=-100,
                msg='http请求失败，状态: %s' % rsp.status_code,
                data=dict(),
            )

        json_data = rsp.json()

        if str(json_data['status']) == '0':
            return dict(
                code=-1,
                msg=json_data['message'],
                data=dict(),
            )

        item = json_data['data'][0]
        if str(item['status']) == '0':
            return dict(
                code=-2,
                msg=json_data['message'],
                data=dict(),
            )

        return dict(
            code=0,
            msg='ok',
            # 商户订单号
            data=dict(tx_id=item['corderid']),
        )

    def launch_pay(self, params_dict):
        """
        发起支付
        :return:
        """
        request_data = self.construct_request(params_dict)
        # print('request_data:', request_data)

        url = self.gen_url()
        post_data = '&'.join(["{}={}".format(k, v) for k, v in request_data.items()])

        try:
            current_app.logger.info('ponypay withdraw, url: %s, data: %s', url, post_data)

            rsp = requests.post(url, data=post_data, headers={
                "Content-Type": "application/x-www-form-urlencoded",
            })

            current_app.logger.info('ponypay withdraw, status_code: %s, content: %s', rsp.status_code, rsp.text)
        except:
            current_app.logger.fatal(traceback.format_exc())
            return dict(
                code=-1,
                msg="http请求异常",
                data=dict(),
            )

        return self.parse_response(rsp)


if __name__ == '__main__':
    _data = {
        "tx_id": "14774939",  # 商户代付订单号；
        "amount": "100.00",  # 代付金额，请加手续费5元，实际到账减5元
        "bank_name": "中国建设银行",  # 银行名称
        "bank_account": "陈XX",  # 用户在银行的姓名
        "bank_number": "62270XXXX328",  # 银行账号
        "bank_address": "建设银行"  # 例如：中国银行XXXX支行
    }
    WithdrawRequest(ChannelConfigEnum.CHANNEL_1001).launch_pay(**_data)
