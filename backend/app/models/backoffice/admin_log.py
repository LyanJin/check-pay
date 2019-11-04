import json

from flask import request, g, has_request_context, has_app_context

from app.enums.admin import AdminModuleEnum
from app.extensions import db
from app.libs.model.base import ModelBase
from app.libs.ip_kit import IpKit
from config import DBEnum


class AdminLog(ModelBase):
    """
    后台用户的操作日志记录
    """
    __bind_key__ = DBEnum.BACK.value

    _create_time = db.Column('create_time', db.Integer, nullable=False, comment="创建时间", index=True)
    account = db.Column(db.String(32), comment="操作员", index=True)
    url = db.Column(db.String(128), comment="请求路径")
    _ip = db.Column('ip', db.BigInteger, comment="ip")
    _module = db.Column('module', db.SmallInteger, comment="模块")
    model = db.Column(db.String(32), comment="模型")
    model_id = db.Column(db.BigInteger, comment="模型id")
    _data_before = db.Column('data_before', db.Text, comment="原内容")
    _data_after = db.Column('data_after', db.Text, comment="修改之后的内容")

    @property
    def data_before(self) -> dict:
        return json.loads(self._data_before)

    @data_before.setter
    def data_before(self, value: dict):
        self.model = value.pop('model')
        self.model_id = value.pop('model_id')
        self._data_before = json.dumps(self.covert_data_to_dict(value))

    @property
    def data_after(self):
        return json.loads(self._data_after)

    @data_after.setter
    def data_after(self, value: dict):
        self.model = value.pop('model')
        self.model_id = value.pop('model_id')
        self._data_after = json.dumps(self.covert_data_to_dict(value))

    @property
    def ip(self) -> str:
        """
        整形IP转为字符串
        :return:
        """
        return IpKit.int_to_ip(self._ip)

    @ip.setter
    def ip(self, value: str):
        """
        存储为整数
        :param value:
        :return:
        """
        self._ip = IpKit.ip_to_int(value)

    @property
    def module(self) -> AdminModuleEnum:
        """
        操作内容，返回dict
        :return:
        """
        return AdminModuleEnum(self._module)

    @module.setter
    def module(self, value: AdminModuleEnum):
        """
        设置内容，存储时转换为json存储
        :param value:
        :return:
        """
        self._module = value.value

    @classmethod
    def get_extra_params(cls):
        if not has_request_context() or not has_app_context():
            return dict()

        return dict(
            url=request.path,
            module=AdminModuleEnum.get_module_by_path(),
            account=g.user.account if g.get('user') else '',
            ip=IpKit.get_remote_ip(),
        )

    @classmethod
    def add_log(cls, account: str, ip: str, module: AdminModuleEnum, data_before: dict, data_after: dict):
        """
        添加日志
        :param account:
        :param ip:
        :param module:
        :param data_before:
        :param data_after:
        :return:
        """
        with db.auto_commit():
            log = cls()
            log.account = account
            log.ip = ip
            log.module = module
            log.content = dict(
                data_before=data_before,
                data_after=data_after,
            )
            db.session.add(log)

        return log

    @classmethod
    def query_log(cls, begin_time, end_time, **kwargs):
        """
        查询日志，必须输入时间
        :param begin_time: 开始时间，可以是datetime，也可以是date
        :param end_time: 结束时间，可以是datetime，也可以是date
        :return:
        """
        return cls.query_by_create_time(begin_time, end_time).filter_by(**kwargs)

    @classmethod
    def query_by_account(cls, begin_time, end_time, account):
        """
        根据时间和账号查询日志
        :param begin_time:
        :param end_time:
        :param account:
        :return:
        """
        return cls.query_log(begin_time, end_time, account=account)
