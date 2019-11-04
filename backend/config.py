import os
import logging
from datetime import timedelta
from enum import unique

from app.enums.base_enum import BaseEnum

BASEDIR = os.path.abspath(os.path.dirname(__file__))
TEMPLATE_FOLDER = os.path.join(BASEDIR, 'templates')


@unique
class EnvironEnum(BaseEnum):
    DEVELOPMENT = 'development'
    TESTING = 'testing'
    PRODUCTION = 'production'

    @classmethod
    def is_local_evn(cls, value):
        return value in [cls.DEVELOPMENT.value, ]

    @classmethod
    def is_production(cls, value):
        return value in [cls.PRODUCTION.value]


@unique
class ServiceEnum(BaseEnum):
    CASHIER = 'cashier'
    GATEWAY = 'gateway'
    BACKOFFICE = 'backoffice'
    SCHEDULER = 'scheduler'
    CONFIGURATION = 'configuration'
    CALLBACK = 'callback'
    MERCHANTOFFICE = 'merchantoffice'
    CELERY = 'celery'

    @classmethod
    def is_job_service(cls, value):
        return value in [
            cls.SCHEDULER.value,
        ]

    @classmethod
    def is_celery_service(cls, value):
        return value in [
            cls.CELERY.value,
        ]

    @classmethod
    def is_daemon_service(cls, value):
        return value in [
            cls.CONFIGURATION.value,
        ]

    @classmethod
    def is_backoffce(cls, value):
        return value in [cls.BACKOFFICE.value, cls.MERCHANTOFFICE.value]

    @classmethod
    def is_callback(cls, value):
        return cls.CALLBACK.value == value

    @classmethod
    def is_merchantoffice(cls, value):
        return cls.MERCHANTOFFICE.value == value


FLASK_ENV = os.getenv('FLASK_ENV') or EnvironEnum.DEVELOPMENT.value
FLASK_SERVICE = os.getenv('FLASK_SERVICE') or ServiceEnum.CALLBACK.value
SENTRY_DSN = os.getenv('SENTRY_DSN') or ''


@unique
class MerchantTypeEnum(BaseEnum):
    """商户类型"""
    NORMAL = 1
    TEST = 2


@unique
class MerchantEnum(BaseEnum):
    """商户"""
    TEST = 100
    QF2 = 101
    QF3 = 102
    # 之夜-代理-01
    ZYPROXY01 = 103
    # 扑克之城
    COP = 104

    # API类商户
    # 豪门
    TEST_API = 200
    HAOMEN = 203

    @property
    def is_api_merchant(self):
        return self in [
            self.TEST_API,
            self.HAOMEN,
        ]

    @classmethod
    def get_api_merchants(cls):
        return [x for x in cls if x.is_api_merchant]

    @property
    def mch_type(self):
        """
        判断是否是测试商户
        :return:
        """
        if self.is_test:
            return MerchantTypeEnum.TEST
        else:
            return MerchantTypeEnum.NORMAL

    @classmethod
    def get_name_type_pairs(cls):
        rst = list()
        for x in cls:
            rst.append(dict(
                name=x.name,
                type=x.mch_type.value,
            ))
        return rst

    @property
    def is_test(self):
        return self in [self.TEST, self.TEST_API]


@unique
class DBEnum(BaseEnum):
    """
    数据库名称配置
    """
    # 业务主库
    MAIN = 'MAIN'
    # 备份数据库
    BACK = 'BACK'

    # # 以下是商户独立的数据库
    # TEST = MerchantEnum.TEST.name
    # QF2 = MerchantEnum.QF2.name
    # QF3 = MerchantEnum.QF3.name
    # HAOMEN = MerchantEnum.HAOMEN.name

    def get_db_name(self):
        """
        新增商户后，一定要在这里配置好商户对应的数据库
        :return:
        """
        return {
            self.MAIN.name: 'main_db',
            self.BACK.name: 'back_db',
            # self.TEST.name: 'merchant_test',
            # self.QF2.name: 'merchant_qf2',
            # self.QF3.name: 'merchant_qf3',
            # self.HAOMEN.name: 'merchant_haomen',
        }.get(self.name)

    @classmethod
    def is_valid(cls, name):
        return name.upper() in cls.__members__

    @classmethod
    def join_mysql_uri(cls, db_name):
        return "mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}?charset=utf8mb4".format(
            user=os.environ.get('DB_USER') or 'root',
            password=os.environ.get('DB_PASSWORD') or 'root',
            host=os.environ.get('DB_HOST') or 'localhost',
            port=os.environ.get('DB_PORT') or 3306,
            db_name=db_name,
        )

    @classmethod
    def join_sqlite_uri(cls, db_name):
        return 'sqlite:///' + os.path.join(BASEDIR, 'sqlites/%s.sqlite?check_same_thread=False' % db_name)

    @classmethod
    def get_db_uri(cls, db_enum):
        """
        如果要单元调试某个测试用例，手动打开注释 unit_test = True，测试完毕后一定要注释回去
        :param db_enum:
        :return:
        """
        unit_test = os.environ.get('UNIT_TEST')
        # unit_test = True
        if unit_test and EnvironEnum.is_local_evn(FLASK_ENV):
            # 本地自动化的单元测试，使用sqlite
            return cls.join_sqlite_uri(db_enum.get_db_name())
        return cls.join_mysql_uri(db_enum.get_db_name())

    @classmethod
    def get_main_config(cls):
        return cls.get_db_uri(cls.MAIN)

    @classmethod
    def get_binds_config(cls):
        return {e.value: cls.get_db_uri(e) for e in cls if e != cls.MAIN}


class MerchantDomainConfig:
    if FLASK_ENV == EnvironEnum.PRODUCTION.value:
        CALLBACK_DOMAIN = 'callback.epay12306.com'
        GATEWAY_DOMAIN = 'gateway.epay12306.com'
        # 备用域名
        CALLBACK_DOMAIN2 = 'callback.sxhcwb.com'
        GATEWAY_DOMAIN2 = 'gateway.sxhcwb.com'
    else:
        CALLBACK_DOMAIN = 'callback.epay1001.com'
        GATEWAY_DOMAIN = 'gateway.epay1001.com'

    if FLASK_ENV == EnvironEnum.PRODUCTION.value:
        __domains = {
            MerchantEnum.TEST: [
                'cashier-test.epay12306.com',
            ],
            MerchantEnum.QF2: [
                'cashier-qf2.epay12306.com',
            ],
            MerchantEnum.QF3: [
                'cashier-qf3.epay12306.com',
            ],
            MerchantEnum.ZYPROXY01: [
                'zyproxy01.epay12306.com',
            ],
            MerchantEnum.COP: [
                'cop.epay12306.com',
            ],
        }
    else:
        __domains = {
            MerchantEnum.TEST: [
                '127.0.0.1',
                'localhost',
                '192.168.1.4',
                '172.16.1.107',
                '192.168.1.16',
                '192.168.1.9',
                '192.168.1.50',
                '192.168.1.5',
                'cashier-test.epay1001.com',
            ],
            MerchantEnum.QF2: [
                'cashier-qf2.epay1001.com',
            ],
            MerchantEnum.QF3: [
                'cashier-qf3.epay1001.com',
            ],
            MerchantEnum.ZYPROXY01: [
                'zyproxy01.epay1001.com',
            ],
            MerchantEnum.COP: [
                'cop.epay1001.com',
            ],
        }

    @classmethod
    def get_all_domains(cls):
        import itertools
        return list(itertools.chain(*cls.__domains.values()))

    @classmethod
    def validate_config(cls):
        domains = cls.get_all_domains()
        if len(domains) != len(set(domains)):
            raise Exception('repeated domain config')

    @classmethod
    def get_merchant(cls, domain) -> MerchantEnum:
        """
        根据域名获取商户名称
        :param domain:
        :return:
        """
        for name, domains in cls.__domains.items():
            if domain in domains:
                return name

    @classmethod
    def get_domains(cls, merchant: MerchantEnum):
        """
        获取商户下的所有的域名
        :param merchant:
        :return:
        """
        if merchant.is_api_merchant:
            return [cls.get_gateway_domain(merchant)]
        return list(cls.__domains[merchant])

    @classmethod
    def get_latest_domain(cls, merchant: MerchantEnum):
        """
        获得最新的一个域名
        :param merchant:
        :return:
        """
        return cls.get_domains(merchant)[-1]

    @classmethod
    def get_gateway_domain(cls, merchant: MerchantEnum = None):
        return cls.GATEWAY_DOMAIN

    @classmethod
    def get_callback_domain(cls, merchant: MerchantEnum = None):
        return cls.CALLBACK_DOMAIN


# 检查配置的域名是否重复
MerchantDomainConfig.validate_config()


class Config:
    # 为了使所有响应返回统一的格式（APIException），json响应里面不要包含message变量
    # flask_restplus/api.py:595
    #         include_message_in_response = current_app.config.get("ERROR_INCLUDE_MESSAGE", True)
    # ERROR_INCLUDE_MESSAGE = False

    DEBUG = False
    TESTING = False

    SECRET_KEY = os.getenv('SECRET_KEY') or 'hard to guess string'

    FLASK_ENV = ENV = FLASK_ENV
    FLASK_SERVICE = FLASK_SERVICE

    SENTRY_DSN = SENTRY_DSN

    SCHEDULER_API_ENABLED = True

    # session过期时间
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=5)
    # LOGIN_DISABLED = True

    # http://www.pythondoc.com/flask-sqlalchemy/config.html
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = DBEnum.get_main_config()
    SQLALCHEMY_BINDS = DBEnum.get_binds_config()

    REDIS_URL = os.environ.get('REDIS_URL') or "redis://localhost:6379/0"

    # 接口频率限制
    RATELIMIT_STORAGE_URL = REDIS_URL

    # celery队列配置
    BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL

    # ELK 日志端口
    LOG_STASH_PORT = 5000
    # 测试环境，日志报到公网测试服
    LOG_STASH_HOST = 'ec2-18-162-134-194.ap-east-1.compute.amazonaws.com'
    # info级别上报给ELK
    LOG_STASH_LEVEL = logging.ERROR

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True

    REDIS_URL = os.environ.get('REDIS_URL') or "redis://localhost:6379/0"
    RATELIMIT_STORAGE_URL = "memory://"

    LOGGER_CONF = dict(
        path='logs',
        filename='flask.log',
        level=logging.DEBUG,
        format='[%(asctime)s] %(levelname)s in %(pathname)s %(lineno)s: %(message)s',
        keep_days=7,
    )


class TestingConfig(Config):
    TESTING = True

    LOGGER_CONF = dict(
        path='logs',
        filename='flask.log',
        level=logging.DEBUG,
        format='[%(asctime)s] %(levelname)s in %(pathname)s %(lineno)s: %(message)s',
        keep_days=7,
    )

    SQLALCHEMY_ENGINE_OPTIONS = dict(
        # 连接池大小
        pool_size=10,
        # 可溢出的链接数
        max_overflow=10,
        # 连接空闲多久后回收释放
        pool_recycle=60 * 5,
        # 从连接池获取连接的超时时间，5s获取不到就失败
        pool_timeout=5,
        # 执行真实业务前检查连接是否断开
        pool_pre_ping=True,
        # 使用last in first out，从连接池中取用最新创建的链接
        pool_use_lifo=True,
    )


class ProductionConfig(Config):
    LOGGER_CONF = dict(
        path='logs',
        filename='flask.log',
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)s in %(pathname)s %(lineno)s: %(message)s',
        keep_days=7,
    )

    SQLALCHEMY_ENGINE_OPTIONS = dict(
        # 连接池大小
        pool_size=100,
        # 可溢出的链接数
        max_overflow=0,
        # 连接空闲多久后回收释放
        pool_recycle=60 * 5,
        # 从连接池获取连接的超时时间，5s获取不到就失败
        pool_timeout=5,
        # 执行真实业务前检查连接是否断开
        pool_pre_ping=True,
        # 使用last in first out，从连接池中取用最新创建的链接
        pool_use_lifo=True,
    )


flask_config = {
    EnvironEnum.DEVELOPMENT.value: DevelopmentConfig,
    EnvironEnum.TESTING.value: TestingConfig,
    EnvironEnum.PRODUCTION.value: ProductionConfig,
}
