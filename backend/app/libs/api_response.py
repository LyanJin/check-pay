from app.libs.api_exception import APIException
from app.libs.doc_response import ResponseDoc


class ResponseBase(APIException):
    """
    响应基类，结合异常类和响应文档类
    主要封装了动态生成doc的函数 gen_doc
    """

    @classmethod
    def gen_doc(cls, api):
        """
        为指定api动态生成文档
        :param api:
        :return:
        """
        return ResponseDoc.gen_response_model(api, cls)
