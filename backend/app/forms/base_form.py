"""
表单验证封装
"""
import functools

from flask import request, current_app
from wtforms import Form, StringField
from wtforms.compat import iteritems

from app.libs.error_code import ParameterException
from app.libs.ip_kit import IpKit


class BaseForm(Form):
    client_ip = StringField(description="客户端真实IP地址")
    user_agent = StringField(description="客户端User-Agent")

    @classmethod
    def get_json_data(cls):
        return request.get_json(silent=True) or dict()

    @property
    def json_data(self):
        return self.get_json_data()

    @classmethod
    def get_from_data(cls):
        return dict([(k, v) for k, v in request.form.items()])

    @property
    def form_data(self):
        return self.get_from_data()

    @classmethod
    def get_data(cls):
        return cls.get_json_data() or cls.get_from_data() or request.args.to_dict()

    @classmethod
    def load_request_data(cls):
        data = cls.get_data()
        # 取出IP地址
        data['client_ip'] = IpKit.get_remote_ip()
        # 客户端的类型
        data['user_agent'] = request.headers.get('User-Agent')
        return data

    @classmethod
    def request_validate(cls):
        """
        载入request，并验证表单
        :return:
        """
        data = cls.load_request_data()
        # current_app.logger.info('request, path: %s, data: %s, kwargs: %s', request.path, data, kwargs)
        return cls(data=data).validate_for_api()

    def validate_for_api(self):
        if not super(BaseForm, self).validate():
            message = {'': ""}
            for name, field in iteritems(self._fields):
                if field.errors:
                    current_app.logger.error('form: %s, name: %s, errors: %s, json_data: %s',
                        self.__class__.__name__, name, field.errors, self.json_data)
                    if isinstance(field, StringField):
                        message = {name: field.errors[0]}
                        break
                    if isinstance(field.errors, list):
                        message = {field.name: field.errors[0]}
                        break
                    elif isinstance(field.errors, dict):
                        for _, _field in iteritems(field.errors):
                            if _field:
                                message = {field.name: _field[0]}
                                break
            print("form: %s, name: %s, errors: %s, json_data: %s" % (self.__class__.__name__, name, field.errors, self.json_data))
            return self, ParameterException(message=list(message.values())[0])
        return self, None


def stop_validate_if_error_occurred(validate_func):
    """
    如果前面的表单验证器已经验证失败，不需要继续执行验证
    :param validate_func:
    :return:
    """

    @functools.wraps(validate_func)
    def __validate(form, *args, **kwargs):
        if form.errors:
            # print('stop validator: %s' % validate_func.__name__)
            return
        return validate_func(form, *args, **kwargs)

    return __validate
