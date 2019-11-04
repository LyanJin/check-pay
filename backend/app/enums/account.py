"""
账号相关枚举类型定义
"""
from enum import unique

from app.enums.base_enum import BaseEnum


@unique
class AccountTypeEnum(BaseEnum):
    """账户类型"""
    NONE = 0  # 未知类型
    MOBILE = 1
    EMAIL = 2
    ACCOUNT = 3


@unique
class AuthTypeEnum(BaseEnum):
    """鉴权类型"""
    # 使用密码鉴权
    PASSWORD = 1
    # 使用短信验证码鉴权
    SMS_CODE = 2


@unique
class CacheKeyTypeEnum(BaseEnum):
    """Cache type"""
    AUTH_KEY = 1
    AUTH_KEY_COUNT = 2


@unique
class AccountStateEnum(BaseEnum):
    """账号状态"""
    INACTIVE = 0
    ACTIVE = 1


@unique
class AccountFlagEnum(BaseEnum):
    """账号标签"""
    NORMAL = 0
    VIP = 1

    @property
    def is_vip(self):
        return self == self.VIP


@unique
class UserPermissionEnum(BaseEnum):
    """用户权限"""
    BINDCARD = 0x1 << 1
    DEPOSIT = 0x1 << 2
    WITHDRAW = 0x1 << 3
    TRANSFER = 0x1 << 4

    def desc(self):
        return {
                   self.BINDCARD: "绑定银行卡",
                   self.WITHDRAW: "提现",
                   self.DEPOSIT: "充值",
                   self.TRANSFER: "转账",
               }.get(self) or self.name

    def has_permission(self, value):
        and_value = self.value & value
        # print(value, self.value, and_value)
        # print(bin(value), bin(self.value), bin(and_value))
        return and_value == self.value

    @classmethod
    def parse_permissions(cls, value):
        perms = list()
        for perm in cls:
            if perm.has_permission(value):
                perms.append(perm)
        return perms

    @classmethod
    def join_permissions(cls, values):
        perms = 0
        for perm in values:
            perms |= perm.value
        return perms


if __name__ == '__main__':
    pps = UserPermissionEnum.join_permissions([UserPermissionEnum.WITHDRAW, UserPermissionEnum.BINDCARD])
    print(pps)
    print(UserPermissionEnum.DEPOSIT.has_permission(pps))
    print(UserPermissionEnum.WITHDRAW.has_permission(pps))
    print(UserPermissionEnum.BINDCARD.has_permission(pps))
    print(UserPermissionEnum.parse_permissions(pps))
