import socket
import struct

from flask import request, has_request_context
from flask_limiter.util import get_ipaddr


class IpKit:
    """
    IP整形和字符串的转换
    """

    @classmethod
    def is_private_ip(cls, ip: str):
        return ip.startswith('127.') or ip.startswith('10.') or ip.startswith('192.') or ip.startswith(
            '172.') or ip in ['0.0.0.0', 'localhost']

    @classmethod
    def ip_to_int(cls, ip: str) -> int:
        return socket.ntohl(struct.unpack("I", socket.inet_aton(str(ip)))[0])

    @classmethod
    def int_to_ip(cls, ip: int) -> str:
        return socket.inet_ntoa(struct.pack('I', socket.htonl(ip)))

    @classmethod
    def get_remote_ip(cls):
        if not has_request_context():
            return '127.0.0.1'

        # 'HTTP_X_REAL_IP': '10.255.0.3',
        # 'HTTP_X_FORWARDED_FOR': '114.198.145.117, 10.255.0.3',
        # 'HTTP_X_FORWARDED_PROTO': 'http',
        # 'HTTP_X_FORWARDED_PORT': '443',
        return get_ipaddr()
