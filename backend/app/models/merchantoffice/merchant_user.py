from werkzeug.security import generate_password_hash, check_password_hash

from app.libs.model.base import ModelBase
from config import DBEnum
from app.extensions import db


class MerchantUser(ModelBase):
    __bind_key__ = DBEnum.BACK.value

    id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    account = db.Column(db.String(32), comment="商户名称", unique=True)

    _password = db.Column('password', db.String(100), comment="登陆密码")

    @property
    def mid(self):
        return self.id

    @mid.setter
    def mid(self, raw_id):
        self.id = raw_id

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, raw_pwd):
        self._password = generate_password_hash(raw_pwd)

    @classmethod
    def register_account(cls, mid, account, password):
        """
        注册账号
        :param account:
        :param login_pwd:
        :return:
        """
        user = cls()
        user.mid = mid
        user.account = account
        user.password = password

        with db.auto_commit():
            db.session.add(user)

        return user

    def reset_password(cls, account=None, mid=None, password=None):
        """
        修改密码
        :param account:
        :param mid:
        :param password:
        :return:
        """
        with db.auto_commit():
            if mid:
                user = cls.query_user(mid=mid)
            else:
                user = cls.query_user(account=account)
            if user is not None:
                user.password = password
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

        return user.check_password(password)

    def check_password(self, raw_pwd):
        return check_password_hash(self.password, raw_pwd)

    @classmethod
    def query_user(cls, mid=None, account=None):
        """
        查询用户
        :param mid:
        :param account:
        :return:
        """
        if mid:
            kwargs = dict(id=int(mid))
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
