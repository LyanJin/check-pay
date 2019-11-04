import functools

from app.libs.error_code import Forbidden
from app.libs.ip_kit import IpKit


def check_ip_in_white_list(ip_list: list):
    """
    检查IP是否在白名单内
    :param ip_list:
    :return:
    """
    def _check_ip_in_white_list(func):
        @functools.wraps(func)
        def __check_ip_in_white_list(*args, **kwargs):
            ip = IpKit.get_remote_ip()
            if IpKit.is_private_ip(ip) or ip in ip_list:
                return func(*args, **kwargs)
            return Forbidden().as_response()
        return __check_ip_in_white_list
    return _check_ip_in_white_list
