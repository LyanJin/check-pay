"""
环境变量配置
"""
import os

FLASK_ENV = os.getenv('FLASK_ENV')
FLASK_SERVICE = os.getenv('FLASK_SERVICE')
SENTRY_DSN = os.getenv('SENTRY_DSN')
