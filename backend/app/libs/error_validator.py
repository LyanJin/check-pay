"""错误码装饰器，判断错误码重复以及对错误码集合处理
"""


class ErrorCodeValidator:
    error_codes = dict()
    http_codes = dict()
    # 默认的共有的响应
    default_response = list()
    # 只有登录之后才有的响应错误码
    login_response = list()

    @classmethod
    def __check_code_repeat(cls, response_cls):
        """
        error_code 为0时，可以重复定义响应类，每个接口的返回的业务模型都不一样
        error_code 不为0时，不允许重复定义响应类，因为每个错误码应该都有唯一的错误特性，应该给客户端准确的错误信息提示
        :param response_cls:
        :return:
        """
        if response_cls.error_code in cls.error_codes:
            raise ValueError("repeated error code: %s, response_cls: %s" % (response_cls.error_code, response_cls))

        cls.error_codes[response_cls.error_code] = response_cls

    @classmethod
    def check(cls, is_default=False, login_default=False):
        """
        检查错误码是否重复
        :param is_default:
        :param login_default: 登录之后共有的响应类
        :return:
        """
        def __inner_decorate(response_cls):
            cls.__check_code_repeat(response_cls)

            cls.http_codes[response_cls.code] = response_cls

            if is_default and response_cls not in cls.default_response:
                cls.default_response.append(response_cls)

            if login_default and response_cls not in cls.login_response:
                cls.login_response.append(response_cls)

            return response_cls
        return __inner_decorate

    @classmethod
    def get_class(cls, http_code):
        """
        根据http 状态码获取响应类
        :param http_code:
        :return:
        """
        return cls.http_codes.get(http_code)

    @classmethod
    def get_default_response_classes(cls):
        """
        默认的响应类
        :return:
        """
        return cls.default_response

    @classmethod
    def get_login_response_classes(cls):
        """
        登录之后共有的响应类
        :return:
        """
        return cls.login_response
