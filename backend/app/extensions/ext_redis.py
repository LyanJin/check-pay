"""redis实例，开发环境使用 FlaskRedis
"""
from flask_redis import FlaskRedis

from config import EnvironEnum
import config

redis = FlaskRedis()

if config.FLASK_ENV == EnvironEnum.DEVELOPMENT.value:
    from fakeredis import FakeStrictRedis
    redis = FlaskRedis.from_custom_provider(FakeStrictRedis)
