import os

from yunpian_python_sdk.model import constant as YC
from yunpian_python_sdk.ypclient import YunpianClient


class SMSToolKit:
    YP_API_CODE = os.getenv('YP_API_CODE')

    def __init__(self, apicode=None):
        apicode = apicode or self.YP_API_CODE or ''
        # 需要使用海外服务器
        self.client = YunpianClient(apicode, {YC.YP_SMS_HOST: "https://us.yunpian.com"})

    def send_sms(self, phone_number, message):
        """
        通过云片网发送短信        
        :param phone_number:
        :param message:
        :return:
        """

        # param = {YC.MOBILE: '18616020***', YC.TEXT: '【云片网】您的验证码是1234'}
        # param = {YC.MOBILE: urllib.parse.quote(phone_number), YC.TEXT: message}
        param = {YC.MOBILE: phone_number, YC.TEXT: message}
        r = self.client.sms().single_send(param)
        # 获取返回结果, 返回码:r.code(),返回码描述:r.msg(),API结果:r.data(),其他说明:r.detail(),调用异常:r.exception()
        # 短信:clnt.sms() 账户:clnt.user() 签名:clnt.sign() 模版:clnt.tpl() 语音:clnt.voice() 流量:clnt.flow()

        return r and r.code() == 0


if __name__ == '__main__':
    """
    测试需要先设置环境变量
    %2b86189755320
    09398451306
    """
    # SMSToolKit().send_sms("+86189755320", "【壹Pay】您的验证码是5041")
    SMSToolKit().send_sms("+6391666602",
                          "【ecashier】Verification code 1356,valid within 5 minutes. For your protection,do not share the code with anyone")
