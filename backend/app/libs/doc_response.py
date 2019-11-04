"""给http响应生成文档，装饰APIException的派生类
"""
from collections import Iterable

from flask_restplus import fields

from app.libs.error_validator import ErrorCodeValidator


class ResponseDoc:

    @classmethod
    def gen_response_model(cls, api, response_cls):
        """
        给响应类生成文档模型
        :param api:
        :param response_cls:
        :return:
        """
        model_dict = {
            'error_code': fields.Integer(description='错误码', example=response_cls.error_code),
            'message': fields.String(description='错误提示', example=response_cls.message),
        }
        if response_cls.doc_path:
            model_dict.update(request=fields.String(description='method /path', example="GET /test"))
        if response_cls.data_model:
            model_dict.update(data=fields.Nested(response_cls.data_model))

        return api.model(response_cls.__name__, model_dict)

    @classmethod
    def response(cls, ns, api, exceptions=None, login=True, default=True, multi_code=[200, 401]):
        """
        给Resource装饰异常文档
        ns.response 本来就是一个装饰器，重新封装之后，支持多个response同时注册，并且动态为指定api注册响应
        :param ns:
        :param api:
        :param exceptions:
        :param login: 标记该接口是否是登录之后才能调用的接口
        :param default: 默认响应描述
        :param multi_code: 有多个自定义错误码的http状态码
        :return:
        """
        if exceptions is None:
            exceptions = list()

        if not isinstance(exceptions, Iterable):
            exceptions = [exceptions]

        if default:
            exceptions.extend(list(ErrorCodeValidator.get_default_response_classes()))

        if login:
            exceptions.extend(list(ErrorCodeValidator.get_login_response_classes()))

        def __response_wrapper(resource_cls):
            """
            :param resource_cls: 本装饰的资源类
            :return:
            """
            for response_cls in exceptions:
                ns.response(
                    # http状态码,自定义错误码
                    response_cls.error_code if response_cls.code in multi_code else response_cls.code,
                    # 错误描述
                    response_cls.error_name,
                    # 指定api动态生成model, ResponseBase.gen_doc
                    response_cls.gen_doc(api),
                )(resource_cls)  # 本来就是装饰器，所有要传入被装饰的resource类
            return resource_cls

        return __response_wrapper

    # 用于检查错误码重复定义
    error_codes = set()

    @classmethod
    def __check_code_repeat(cls, response_cls):
        """
        error_code 为0时，可以重复定义响应类，每个接口的返回的业务模型都不一样
        error_code 不为0时，不允许重复定义响应类，因为每个错误码应该都有唯一的错误特性，应该给客户端准确的错误信息提示
        :param response_cls:
        :return:
        """
        if response_cls.error_code > 0 and response_cls.error_code in cls.error_codes:
            raise ValueError("repeated error code: %s" % response_cls.error_code)

        cls.error_codes.add(response_cls.error_code)

    @classmethod
    def gen_marshal(cls, response_cls):
        """
        检查错误码是否重复
        :param response_cls:
        :return:
        """
        cls.__check_code_repeat(response_cls)
        return response_cls
