from flask import request


class UrlKit:

    @classmethod
    def is_localhost(cls):
        return 'localhost' in request.host or '127.0.0.1' in request.host or '0.0.0.0' in request.host

    @classmethod
    def get_scheme(cls):
        if cls.is_localhost():
            return 'http://'
        else:
            return 'https://'

    @classmethod
    def join_host_path(cls, path, host=None):
        """
        组装host和path
        :param path:
        :param host:
        :return:
        """
        return cls.get_scheme_host(host) + path

    @classmethod
    def get_scheme_host(cls, host=None):
        if cls.is_localhost():
            host = request.host

        if not host:
            host = request.host.split(':')[0]

        scheme = cls.get_scheme()

        return ''.join([scheme, host])

    @classmethod
    def headers_to_dict(cls, headers):
        return dict([(k, v) for k, v in headers.items()])
