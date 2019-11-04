"""主程序的执行入口
"""
import gevent.monkey

# gevent猴子补丁，在导入任何其它库之前调用

gevent.monkey.patch_all()

import config
from app.app import FlaskApp
from app.extensions.ext_celery import flask_celery

flask_app = FlaskApp.create_app(config.FLASK_SERVICE, config.FLASK_ENV)
