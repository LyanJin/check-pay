"""
用户基本信息
"""
from typing import List

from werkzeug.security import generate_password_hash, check_password_hash

from app.caches.user_flag import UserFlagCache
from app.enums.account import AccountStateEnum, AccountTypeEnum, AccountFlagEnum, UserPermissionEnum
from app.extensions import db
from app.libs.model.base import ModelBase, MerchantBase
from app.models.balance import UserBalance
from config import MerchantEnum


class GlobalUid(ModelBase):
    """
    全局用户ID表
    """
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True, comment='自增主键')
    _merchant = db.Column('merchant', db.Integer, comment="商户", nullable=False)

    @property
    def merchant(self) -> MerchantEnum:
        return MerchantEnum(self._merchant)

    @merchant.setter
    def merchant(self, value: MerchantEnum):
        self._merchant = value.value

    @classmethod
    def make_uid(cls, merchant: MerchantEnum):
        with db.auto_commit():
            global_uid = cls()
            global_uid.merchant = merchant
            db.session.add(global_uid)

        return global_uid.id

    @classmethod
    def get_merchant(cls, uid):
        obj = cls.query.filter(cls.id == uid).first()
        if obj:
            return obj.merchant
        return ''


class UserBindInfo(ModelBase):
    id = db.Column(db.Integer, primary_key=True, autoincrement=False, comment='用户ID', nullable=False)
    name = db.Column(db.String(64), comment="名称", nullable=False)
    account = db.Column(db.String(32), comment="账号", nullable=False, index=True)
    _bind_type = db.Column('bind_type', db.SmallInteger, comment="绑定类型", nullable=False)
    _merchant = db.Column('merchant', db.Integer, comment="商户ID", nullable=False)

    __table_args__ = (
        # 联合唯一索引
        db.UniqueConstraint('name', 'bind_type', 'merchant', name='uix_user_bind_name_bind_type_merchant'),
    )

    @property
    def uid(self):
        return self.id

    @uid.setter
    def uid(self, value):
        self.id = value

    @property
    def merchant(self) -> MerchantEnum:
        return MerchantEnum(self._merchant)

    @merchant.setter
    def merchant(self, merchant: MerchantEnum):
        self._merchant = merchant.value

    @property
    def bind_type(self):
        """
        返回账户枚举类型
        :return:
        """
        return AccountTypeEnum(self._bind_type)

    @bind_type.setter
    def bind_type(self, e_value):
        """
        传入账户的类型
        :param e_value:
        :return:
        """
        self._bind_type = e_value.value

    @classmethod
    def query_bind_by_uid(cls, uid):
        """
        根据用户ID查询绑定信息
        :param uid:
        :return:
        """
        return cls.query_one(query_fields=dict(id=uid))

    @classmethod
    def query_bind(cls, merchant: MerchantEnum, name, bind_type: AccountTypeEnum = AccountTypeEnum.ACCOUNT):
        return cls.query_one(query_fields=dict(
            _merchant=merchant.value,
            name=name,
            _bind_type=bind_type.value,
        ))

    @classmethod
    def bind_account(cls, uid, merchant: MerchantEnum, account, name,
                     bind_type: AccountTypeEnum = AccountTypeEnum.ACCOUNT):
        obj = cls()
        obj.uid = uid
        obj.merchant = merchant
        obj.name = name
        obj.account = account
        obj.bind_type = bind_type
        cls.commit_models(obj)
        return obj

    @classmethod
    def unbind_account(cls, uid):
        obj = cls.query_bind_by_uid(uid)
        if not obj:
            return False
        cls.commit_models(obj, delete=True)
        return True


class User(MerchantBase):
    """
    用户，按商户分库
    """
    id = db.Column(db.Integer, primary_key=True, autoincrement=False, comment='用户ID，主键但不自增，由全局表生成id')
    _create_time = db.Column('create_time', db.Integer, nullable=False, comment="创建时间", index=True)

    account = db.Column(db.String(32), comment="账号，手机号码/邮箱", nullable=False)
    _ac_type = db.Column('ac_type', db.SmallInteger, default=AccountTypeEnum.NONE.value,
                         comment="账号类型，手机号码/邮箱")
    _state = db.Column('state', db.SmallInteger, default=AccountStateEnum.ACTIVE.value, comment="账号状态")
    _login_pwd = db.Column('login_pwd', db.String(100), comment="登录密码，已加密存储")
    _trade_pwd = db.Column('trade_pwd', db.String(100), comment="支付密码，已加密存储")
    _flag = db.Column('flag', db.SmallInteger, comment="账号状态", nullable=True)
    _permissions = db.Column('permissions', db.SmallInteger, comment="账号权限", nullable=True)

    __table_args__ = (
        # 联合唯一索引
        db.UniqueConstraint('account', 'merchant', name='uix_user_account_mch_name'),
        # 联合索引
        # db.Index('ix_user_account_mch_name', 'account', 'merchant'),
    )

    _merchant = db.Column('merchant', db.Integer, comment="商户ID", nullable=False)

    @property
    def merchant(self) -> MerchantEnum:
        return MerchantEnum(self._merchant)

    @merchant.setter
    def merchant(self, merchant: MerchantEnum):
        self._merchant = merchant.value

    @property
    def permissions(self) -> List[UserPermissionEnum]:
        if not self._permissions:
            return UserPermissionEnum.get_all_enums()
        return UserPermissionEnum.parse_permissions(self._permissions)

    @permissions.setter
    def permissions(self, values: List[UserPermissionEnum]):
        self._permissions = UserPermissionEnum.join_permissions(values)

    @property
    def permission_names(self):
        return [x.name for x in self.permissions]

    def has_permission(self, perm: UserPermissionEnum):
        """
        判断用户是否有权限
        :param perm:
        :return:
        """
        if not self._permissions:
            # 未设置权限，拥有所有权限
            return True
        return perm.has_permission(self._permissions)

    @property
    def flag(self) -> AccountFlagEnum:
        if not self._flag:
            return AccountFlagEnum.NORMAL
        return AccountFlagEnum(self._flag)

    @flag.setter
    def flag(self, value: AccountFlagEnum):
        if value:
            self._flag = value.value

    @property
    def is_official_auth(self):
        return self.flag == AccountFlagEnum.VIP

    @property
    def is_test_user(self):
        """
        是否是测试用户
        :return:
        """
        return self.merchant.is_test

    @property
    def uid(self):
        return self.id

    @property
    def is_active(self):
        return self._state == AccountStateEnum.ACTIVE.value

    @property
    def state(self) -> AccountStateEnum:
        return AccountStateEnum(self._state)

    @state.setter
    def state(self, value: AccountStateEnum):
        self._state = value.value

    @property
    def ac_type(self):
        """
        返回账户枚举类型
        :return:
        """
        return AccountTypeEnum(self._ac_type)

    @ac_type.setter
    def ac_type(self, e_value):
        """
        传入账户的类型
        :param e_value:
        :return:
        """
        if e_value:
            self._ac_type = e_value.value

    @property
    def login_pwd(self):
        """
        登录密码
        :return:
        """
        return self._login_pwd

    @login_pwd.setter
    def login_pwd(self, raw_pwd):
        """
        设置密码时要进行加密
        :param raw_pwd:
        :return:
        """
        if raw_pwd:
            self._login_pwd = generate_password_hash(raw_pwd)

    @property
    def trade_pwd(self):
        """
        交易密码
        :return:
        """
        return self._trade_pwd

    @trade_pwd.setter
    def trade_pwd(self, raw_pwd):
        """
        设置交易密码
        :param raw_pwd:
        :return:
        """
        if raw_pwd:
            self._trade_pwd = generate_password_hash(raw_pwd)

    def has_trade_pwd(self):
        return bool(self.trade_pwd)

    @classmethod
    def generate_model(cls, merchant, account, ac_type: AccountTypeEnum = None, login_pwd=None):
        """
        生成用户模型
        :param merchant:
        :param account:
        :param ac_type:
        :param login_pwd:
        :return:
        """
        user = cls.get_model_obj(merchant=merchant)
        user.account = account
        user.ac_type = ac_type
        user.login_pwd = login_pwd
        user.merchant = merchant
        user.id = 0
        return user

    @classmethod
    def register_account(cls, merchant, account, ac_type: AccountTypeEnum = None, login_pwd=None):
        """
        注册账号
        :param merchant:
        :param account:
        :param ac_type:
        :param login_pwd:
        :return:
        """
        uid = GlobalUid.make_uid(merchant)

        with db.auto_commit():
            user = cls.generate_model(merchant, account, ac_type, login_pwd)
            user.id = uid
            db.session.add(user)

            balance = UserBalance.generate_model(user.uid, merchant)
            db.session.add(balance)

        return user

    @classmethod
    def delete_account(cls, merchant, uid=None, account=None):
        """
        删除账号
        :param uid:
        :param account:
        :param merchant:
        :return:
        """
        with db.auto_commit():
            user = cls.query_user(merchant, uid=uid, account=account)
            db.session.delete(user)

    @classmethod
    def update_user_state(cls, merchant, account=None, uid=None, state=None):
        """
        修改用户状态
        :param merchant:
        :param account:
        :param uid:
        :param state:
        :return:
        """
        with db.auto_commit():
            if not account:
                user = cls.query_user(merchant=merchant, uid=uid)
            else:
                user = cls.query_user(merchant=merchant, account=account)
            if user is not None:
                user.state = state
                db.session.add(user)
                return True
            else:
                return False

    @classmethod
    def update_user_flag(cls, merchant, flag: AccountFlagEnum, account=None, uid=None):
        """
        修改用户标签
        """
        if account:
            user = cls.query_user(merchant=merchant, account=account)
        else:
            user = cls.query_user(merchant=merchant, uid=uid)

        if user is not None:
            user.flag = flag
            cls.commit_models(user)
            UserFlagCache(user.uid).set_flag(flag)
            return True

        return False

    @classmethod
    def update_user_permission(cls, merchant, permissions: List[UserPermissionEnum], account=None, uid=None):
        """
        修改用户权限
        """
        if account:
            user = cls.query_user(merchant=merchant, account=account)
        else:
            user = cls.query_user(merchant=merchant, uid=uid)

        if user is not None:
            user.permissions = permissions
            cls.commit_models(user)
            return True

        return False

    @classmethod
    def reset_password(cls, merchant, account=None, uid=None, login_pwd=None):
        """
        修改密码
        :param merchant:
        :param account:
        :param uid:
        :param login_pwd:
        :return:
        """
        with db.auto_commit():
            if not account:
                user = cls.query_user(merchant=merchant, uid=uid)
            else:
                user = cls.query_user(merchant=merchant, account=account)
            if user is not None:
                user.login_pwd = login_pwd
                db.session.add(user)
                return True
            else:
                return False

    @classmethod
    def verify_login(cls, merchant, account, password):
        """
        账号密码鉴权
        :param merchant:
        :param account:
        :param password:
        :return:
        """
        user = cls.query_user(merchant, account=account)
        if not user:
            return False

        return user.check_login_pwd(password)

    @classmethod
    def verify_password(cls, merchant, uid, password):
        """
        账号密码鉴权
        :param merchant:
        :param uid:
        :param password:
        :return:
        """
        user = cls.query_user(merchant, uid=uid)
        if not user:
            return False

        return user.check_login_pwd(password)

    def check_login_pwd(self, raw_pwd):
        return check_password_hash(self._login_pwd, raw_pwd)

    @classmethod
    def query_user(cls, merchant, uid=None, account=None):
        """
        查询用户
        :param merchant:
        :param uid:
        :param account:
        :return:
        """
        if uid:
            kwargs = dict(id=int(uid))
        elif account:
            kwargs = dict(
                account=account,
            )
        else:
            raise ValueError('parameter error')

        kwargs['_merchant'] = merchant.value

        return cls.query_one(query_fields=kwargs)

    @classmethod
    def set_payment_password(cls, merchant, account=None, uid=None, trade_pwd=None):
        """
        修改密码
        :param merchant:
        :param account:
        :param uid:
        :param trade_pwd:
        :return:
        """
        with db.auto_commit():
            if not account:
                user = cls.query_user(merchant=merchant, uid=uid)
            else:
                user = cls.query_user(merchant=merchant, account=account)
            if user is not None:
                user.trade_pwd = trade_pwd
                db.session.add(user)
                return True
            else:
                return False

    @classmethod
    def verify_payment_password(cls, merchant, uid, password):
        """
        支付密码鉴权
        :param merchant:
        :param uid:
        :param password:
        :return:
        """
        user = cls.query_user(merchant, uid=uid)
        if not user:
            return False

        return user.check_trade_pwd(password)

    def check_trade_pwd(self, raw_pwd):
        """
        验证交易密码
        :param raw_pwd:
        :return:
        """
        if not self._trade_pwd:
            return False

        return check_password_hash(self._trade_pwd, raw_pwd)
