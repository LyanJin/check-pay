"""Flask核心app对象，注册初始化一些app基础服务
"""
import os
import logging

from flask import Flask
from flask_cors import CORS

import config
from app.extensions import db, redis, limiter, scheduler
from app.extensions.ext_celery import flask_celery
from app.extensions.ext_sentry import init_sentry_sdk
from app.libs.logger import MultiProcessSafeDailyRotatingFileHandler, MyTCPLogstashHandler
from app.services import Service


class FlaskApp:

    @classmethod
    def init_logger(cls):
        """
        日志配置
        :return:
        """
        flask_config = config.flask_config[config.FLASK_ENV]
        log_conf = flask_config.LOGGER_CONF

        path = os.path.join(config.BASEDIR, log_conf['path'])
        if not os.path.isdir(path):
            os.makedirs(path)

        logger = logging.getLogger()
        logger.setLevel(log_conf['level'])

        # log to stdout
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(log_conf['format']))
        logger.addHandler(handler)

        # log to local file system
        # emit_tg = config.EnvironEnum.is_production(config.FLASK_ENV)
        emit_tg = not config.EnvironEnum.is_local_evn(config.FLASK_ENV)
        handler = MultiProcessSafeDailyRotatingFileHandler(path, log_conf['filename'], log_conf['keep_days'], emit_tg,
                                                           config.FLASK_ENV)
        handler.setFormatter(logging.Formatter(log_conf['format']))
        logger.addHandler(handler)

        if not config.EnvironEnum.is_local_evn(config.FLASK_ENV):
            # log to ELK
            handler = MyTCPLogstashHandler(
                host=flask_config.LOG_STASH_HOST,
                port=flask_config.LOG_STASH_PORT,
                message_type=config.FLASK_SERVICE,
                tags=[config.FLASK_ENV],
                version=1,
            )
            logger.addHandler(handler)

    @classmethod
    def init_extensions(cls, _app):
        """
        初始化第三方插件
        :param _app:
        :return:
        """
        # extensions init
        # if _app.config['SENTRY_DSN']:
        #     sentry.init_app(_app, logging=_app.logger, level=_app.config['SENTRY_CONFIG']['level'])

        db.init_app(_app)

        redis.init_app(_app)

        # limiter.init_app(_app)

        flask_celery.init_app(_app)

        if config.ServiceEnum.is_job_service(_app.name):
            scheduler.init_app(_app)
            scheduler.start()

    @classmethod
    def create_app(cls, service_name, config_name):
        """
        根据config name创建不同环境下的app
        :param service_name: 服务名称就是app名称，一个服务就是一个app
        :param config_name:
        :return:
        """
        # init logger before sentry
        cls.init_logger()

        # init sentry sdk before flask app created
        if config.SENTRY_DSN:
            init_sentry_sdk(config.SENTRY_DSN, config.FLASK_ENV)

        _app = Flask(service_name, template_folder=config.TEMPLATE_FOLDER)

        _app.config.from_object(config.flask_config[config_name])
        config.flask_config[config_name].init_app(_app)

        # _app.logger.debug(_app.config)

        # extensions init
        cls.init_extensions(_app)

        if config.ServiceEnum.is_celery_service(_app.name):
            Service.auto_discover_db_models(_app)
            Service.auto_discover_celery(_app)

        elif config.ServiceEnum.is_job_service(_app.name) or config.ServiceEnum.is_daemon_service(_app.name):
            Service.auto_discover_db_models(_app)
            Service.auto_discover_api_models(_app)

        else:
            # api init
            Service.init_api(_app)
            # r'/*' 是通配符，让本服务器所有的URL 都允许跨域请求
            CORS(_app, resources=r'/*')

        _app.logger.info('service %s started in env %s', service_name, config_name)

        return _app
