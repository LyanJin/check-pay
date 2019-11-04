from werkzeug.security import generate_password_hash, check_password_hash

from app.enums.account import AccountStateEnum
from app.extensions import db
from app.libs.model.base import ModelBase
from config import DBEnum


class AdminUser(ModelBase):

    __bind_key__ = DBEnum.BACK.value

    account = db.Column(db.String(32), comment="账号", unique=True)
    _state = db.Column('state', db.SmallInteger, default=AccountStateEnum.ACTIVE.value, comment="账号状态")
    _login_pwd = db.Column('login_pwd', db.String(100), comment="登录密码，已加密存储")

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
    def uid(self):
        return self.id

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
        self._login_pwd = generate_password_hash(raw_pwd)

    @classmethod
    def register_account(cls, account, login_pwd):
        """
        注册账号
        :param account:
        :param login_pwd:
        :return:
        """
        user = cls()
        user.account = account
        user.login_pwd = login_pwd

        with db.auto_commit():
            db.session.add(user)

        return user

    @classmethod
    def delete_account(cls, uid=None, account=None):
        """
        删除账号
        :param uid:
        :param account:
        :return:
        """
        with db.auto_commit():
            user = cls.query_user(uid=uid, account=account)
            db.session.delete(user)

    @classmethod
    def reset_password(cls, account=None, uid=None, login_pwd=None):
        """
        修改密码
        :param account:
        :param uid:
        :param login_pwd:
        :return:
        """
        with db.auto_commit():
            if uid:
                user = cls.query_user(uid=uid)
            else:
                user = cls.query_user(account=account)
            if user is not None:
                user.login_pwd = login_pwd
                db.session.add(user)
                return True
            else:
                return False

    @classmethod
    def verify_login(cls, account, password):
        """
        账号密码鉴权
        :param account:
        :param password:
        :return:
        """
        user = cls.query_user(account=account)
        if not user:
            return False

        return user.check_login_pwd(password)

    @classmethod
    def verify_password(cls, uid, password):
        """
        账号密码鉴权
        :param uid:
        :param password:
        :return:
        """
        user = cls.query_user(uid=uid)
        if not user:
            return False

        return user.check_login_pwd(password)

    def check_login_pwd(self, raw_pwd):
        return check_password_hash(self._login_pwd, raw_pwd)

    @classmethod
    def query_user(cls, uid=None, account=None):
        """
        查询用户
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

        return cls.query.filter_by(**kwargs).first()

    @classmethod
    def query_all(cls):
        return cls.query.all()
