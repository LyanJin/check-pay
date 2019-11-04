from flask import request

from app.enums.base_enum import BaseEnum


class AdminModuleEnum(BaseEnum):
    """
    后台模块定义
    """
    SYSTEM = 20
    PERMISSION = 30
    TRADE = 40
    FUNDS = 50
    MERCHANT = 60
    USER = 70
    CHANNEL = 80

    @classmethod
    def get_module_by_path(cls):
        if request.path.startswith('/api/backoffice/v1/merchant'):
            return cls.MERCHANT
        if request.path.startswith('/api/backoffice/v1/channel'):
            return cls.CHANNEL
        if request.path.startswith('/api/backoffice/v1/trade_manage'):
            return cls.TRADE

        return cls.SYSTEM
