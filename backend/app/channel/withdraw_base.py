"""
代付通道
"""
import os


class ProxyPayRequest:
    """
    代付请求
    """
    third_config = None

    def __init__(self, channel_enum):
        self.channel_enum = channel_enum
        self.third_config = channel_enum.conf['_config']

    def launch_pay(self, params_dict: dict):
        """
        发起支付
        :return:
        """
        # 统一返回值
        return dict(
            code=0,
            msg='',
            data=dict(),
        )

    def gen_url(self, *args, **kwargs):
        host = self.third_config['post_url'].strip('/')
        path = self.third_config['withdraw_path'].strip('/')
        return os.path.join(host, path)

    def generate_sign(self, *args, **kwargs):
        """
        生成签名
        :param args:
        :param kwargs:
        :return:
        """
        return

    def construct_request(self, params_dict: dict):
        """
        填写请求参数
        :param params_dict:
        :return:
        """

    def parse_response(self, *args, **kwargs):
        """
        解析响应
        :param args:
        :param kwargs:
        :return:
        """


class ProxyPayCallback:
    """
    代付回调
    """
    third_config = None

    def __init__(self, channel_enum):
        self.channel_enum = channel_enum
        self.third_config = channel_enum.conf['_config']

    def generate_sign(self, *args, **kwargs):
        """
        生成签名
        :param args:
        :param kwargs:
        :return:
        """
        return

    def check_sign(self, *args, **kwargs):
        """
        校验签名
        :param args:
        :param kwargs:
        :return:
        """

    def check_ip(self, client_ip):
        """
        IP白名单校验
        :param client_ip:
        :return:
        """
        return client_ip in self.third_config['white_ip']
