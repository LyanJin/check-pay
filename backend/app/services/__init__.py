"""服务注册和初始化，每个服务一个目录，在发布时用环境变量分开来部署
"""
import json
import time
import traceback

from flask import request, g, Response
from werkzeug.exceptions import HTTPException
from werkzeug.utils import find_modules, import_string

from app.extensions.ext_api import API_CONFIG
from app.libs.error_code import ServerError
from app.libs.api_exception import APIException
from app.libs.error_validator import ErrorCodeValidator
from app.libs.ip_kit import IpKit
from app.libs.url_kit import UrlKit
from app.services.scheduler import DaemonJobs
from config import ServiceEnum

DEBUG_LOG = False


class Service:

    @classmethod
    def init_request_handler(cls, app):

        def output_log():
            # return True
            if ServiceEnum.is_backoffce(app.config['FLASK_SERVICE']):
                return False
            return not app.config['DEBUG'] and 'health/check' not in request.url and 'swaggerui' not in request.url

        @app.before_request
        def before_request():
            if output_log():
                g.before_data = dict()
                g.before_data['time'] = time.time()

        @app.after_request
        def after_request(response: Response):
            try:
                if output_log():
                    request_data = request.json if request.is_json else request.data.decode('utf8')
                    response_data = response.json if response.is_json else response.data.decode('utf8')

                    cost_time = round(time.time() - g.before_data['time'], 5)
                    extra = dict(
                        # request_headers=str(UrlKit.headers_to_dict(request.headers)),
                        status_code=response.status_code,
                        # response_headers=str(UrlKit.headers_to_dict(response.headers)),
                        cost_time=cost_time,
                        client_ip=IpKit.get_remote_ip(),
                    )

                    print('flask path: %s, request_data: %s, response_data: %s, extra: %s' % (
                        request.path, request_data, response_data, extra))

                    if cost_time > 2 or response.status_code == 500:
                        app.logger.error('flask path: %s, request_data: %s, response_data: %s, extra: %s',
                                         request.path, request_data, response_data, extra)
                    else:
                        app.logger.info('flask path: %s, request_data: %s, response_data: %s',
                                        request.path, request_data, response_data, extra=extra)

            except:
                app.logger.error('An error occurred.', exc_info=True)

            return response

        # @app.before_request
        # def before_request():
        #     """
        #     设置session的过期时间，给管理后台使用
        #     :return:
        #     """
        #     session.permanent = True
        #     app.logger.debug('session will expired in %s, path: %s',
        #     app.config['PERMANENT_SESSION_LIFETIME'], request.path)

    @classmethod
    def init_exceptions(cls, app, api):
        """
        全局异常捕获
        :param app:
        :param api:
        :return:
        """

        @api.errorhandler(APIException)
        def api_error(error):
            """
            API层抛出的异常，逻辑异常
            :param error:
            :return:
            """
            app.logger.error(traceback.format_exc())
            return error.as_response()

        @api.errorhandler(HTTPException)
        def http_error(error):
            """
            非业务层的异常
            :param error:
            :return:
            """
            # http异常，非逻辑业务层的异常
            app.logger.error(traceback.format_exc())

            exp_cls = ErrorCodeValidator.get_class(error.code)
            if exp_cls:
                return exp_cls().as_response()

            error = APIException(code=error.code, message=str(error))
            return error.as_response()

        @api.errorhandler
        def default_error_handler(error):
            """
            默认异常处理
            :param error:
            :return:
            """
            app.logger.fatal(traceback.format_exc())
            error = ServerError()
            return error.as_response()

    @classmethod
    def auto_discover_api_models(cls, app):
        """
        遍历service下的所有模块，注册namespace到api上，导入成功即完成注册
        :param app:
        :return:
        """
        service_path = '.'.join([cls.__module__, app.name])

        # app.logger.info('auto discover service: %s', service_path)

        for name in find_modules(service_path, include_packages=False, recursive=True):
            module = import_string(name)

            # app.logger.info('import module: %s', module.__name__)

    @classmethod
    def auto_discover_db_models(cls, app):
        """
        自动发现db model，主要是为了统一进行数据库model同步，所有的服务共享同一个数据库资源
        :param app:
        :return:
        """
        models_path = "app.models"

        # app.logger.info('auto discover service: %s', models_path)

        for name in find_modules(models_path, include_packages=False, recursive=True):
            module = import_string(name)

            # app.logger.info('import module: %s', module.__name__)

    @classmethod
    def auto_discover_celery(cls, app):
        """
        自动发现db model，主要是为了统一进行数据库model同步，所有的服务共享同一个数据库资源
        :param app:
        :return:
        """
        models_path = "app.services.celery"

        # app.logger.info('auto discover service: %s', models_path)

        for name in find_modules(models_path, include_packages=False, recursive=True):
            module = import_string(name)

            # app.logger.info('import module: %s', module.__name__)

    @classmethod
    def init_jobs(cls, app):
        """
        初始化在守护进程运行的任务
        :param app:
        :return:
        """
        cls.auto_discover_db_models(app)
        DaemonJobs(app).init_jobs()

    @classmethod
    def init_api(cls, app):
        """
        初始化服务
        :param app:
        :return:
        """
        api = API_CONFIG[app.name]

        # 初始化app
        api.init_app(app)

        cls.auto_discover_db_models(app)

        # 注册API,导入响应的模块即可完成注册
        cls.auto_discover_api_models(app)

        cls.init_exceptions(app, api)

        cls.init_request_handler(app)
        # if ServiceEnum.is_backoffce(app.name) or ServiceEnum.is_callback(app.name):
        #     cls.init_request_handler(app)

        return api
