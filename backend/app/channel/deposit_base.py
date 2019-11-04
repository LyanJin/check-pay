"""
充值第三方接口处理
"""
from app.enums.third_enum import SdkRenderType
from app.libs.string_kit import RandomString


class DepositRequestBase:
    third_config = dict()

    def __init__(self, channel_enum):
        self.channel_enum = channel_enum
        self.channel_conf = channel_enum.conf
        # third_config里面的属性可以直接从channel_conf里面读取
        self.third_config = self.channel_conf['_config']

    def launch_pay(self, order, params: dict):
        """
        发起支付
        :return:
        """
        # 统一返回值
        return dict(
            code=0,             # 错误码，code=0是没有错误
            msg='',             # 当code不等于0时，填写错误提示信息
            data=dict(
                render_type=SdkRenderType.URL,      # 类型
                render_content=None,                # 内容
                channel_tx_id=None                  # 通道订单号
            ),
        )

    @classmethod
    def construct_headers(cls, params: dict):
        headers = {}
        user_agent = params.get('user_agent')
        if user_agent:
            headers.update({'User-Agent': user_agent})
        return headers

    def gen_url(self, *args, **kwargs):
        """
        生成请求地址
        :param args:
        :param kwargs:
        :return:
        """
        return self.channel_conf.post_url

    def get_secret_key(self):
        return self.channel_conf.secret_key

    @classmethod
    def join_sign_str(cls, params: dict):
        keys = sorted(list(params.keys()))
        return '&'.join(["=".join(map(str, [k, params[k]])) for k in keys])

    def generate_sign(self, params: dict):
        """
        生成签名
        :param params:
        :return:
        """
        raw_str = self.join_sign_str(params)
        raw_str += '&secret_key=' + self.get_secret_key()
        print('raw_str:', raw_str)
        sign = RandomString.gen_md5_string(raw_str.encode('utf8'))
        print('sign:', sign)
        return sign

    def construct_request(self, *args, **kwargs):
        """
        填写请求参数
        :param args:
        :param kwargs:
        :return:
        """

    def parse_response(self, *args, **kwargs):
        """
        解析响应
        :param args:
        :param kwargs:
        :return:
        """


class DepositCallbackBase:
    third_config = dict()

    @classmethod
    def get_secret_key(cls):
        return cls.third_config['secret_key']

    @classmethod
    def generate_sign(cls, *args, **kwargs):
        """
        生成签名
        :param args:
        :param kwargs:
        :return:
        """
        return ''

    @classmethod
    def check_sign(cls, *args, **kwargs):
        """
        签名校验
        :param args:
        :param kwargs:
        :return:
        """
        return False

    @classmethod
    def check_ip(cls, client_ip):
        """
        IP白名单校验
        :param client_ip:
        :return:
        """
        return cls.third_config["white_ip"] and client_ip in cls.third_config["white_ip"]
