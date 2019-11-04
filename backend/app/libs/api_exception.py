"""HTTP异常和异常的文档描述封装
"""
from flask import request, json
from werkzeug.datastructures import Headers
from werkzeug.exceptions import HTTPException


class APIException(HTTPException):
    """
    为API统一返回json数据，即使是异常也返回json
    返回格式示例:
    {
      "error_code": 0,
      "message": "Success",
      "request": "POST /sms/get"
      "data: {
        "result": true
      }
    }
    """
    # HTTP 状态码
    code = 500
    # doc model
    doc_model = None
    # 业务数据的响应模型，异常响应不用指定data_model，返回的数据在 json 的 data 字段里面
    data_model = None
    # 自定义的错误码
    error_code = 999
    # 错误提示信息
    message = 'sorry, we made a mistake (*￣︶￣)!'
    # 业务数据
    bs_data = None
    # 自动添加http method和path
    doc_path = True

    # 这里 data 在rest plus框架里面保存的是http body的json内容，不要给这个属性赋值任何数据
    # 这个属性会被 rest plus底层使用
    # flask_restplus/api.py:637
    #         data = getattr(e, 'data', default_data)
    # flask_restplus/api.py:651
    #         resp = self.make_response(data, code, headers, fallback_mediatype=fallback_mediatype)
    # data = None

    def __init__(self, code=None, message=None, error_code=None, headers=None, bs_data=None):
        """
        异常对象初始化，
        如果提供了参数，使用提供的参数，
        如果没有提供，使用类变量
        :param code:
        :param message:
        :param error_code:
        :param headers:
        :param bs_data: 业务数据
        """
        if code:
            self.code = code
        if error_code:
            self.error_code = error_code
        if message:
            self.message = message

        # 其它http头部信息
        self.headers = headers or []

        # 业务数据
        self.bs_data = bs_data

        super(APIException, self).__init__(message, None)

    def as_response(self):
        """
        返回rest plus 需要的结构
        reference: https://flask-restplus.readthedocs.io/en/stable/errors.html
        :return:
        """
        # api.py:637
        #         data = getattr(e, 'data', default_data)
        # api.py:651
        #         resp = self.make_response(data, code, headers, fallback_mediatype=fallback_mediatype)
        self.headers.extend(self.get_headers())
        headers = Headers(self.headers)
        return self.to_dict(), self.code, headers

    def to_dict(self):
        rst = dict(
            message=self.message,
            error_code=self.error_code,
            request=request.method + ' ' + self.get_url_no_param(),
        )

        if self.bs_data:
            rst.update(data=self.bs_data)

        return rst

    def as_json_response(self):
        """
        json response
        :return:
        """
        self.headers.extend(self.get_headers())
        headers = Headers(self.headers)
        return self.get_body(), self.code, headers

    @property
    def name(self):
        s_name = super(APIException, self).name
        return self.error_name or s_name

    def get_body(self, environ=None):
        text = json.dumps(self.to_dict())
        return text

    def get_headers(self, environ=None):
        """Get a list of headers."""
        return [('Content-Type', 'application/json')]

    @staticmethod
    def get_url_no_param():
        full_path = str(request.full_path)
        main_path = full_path.split('?')
        return main_path[0]


