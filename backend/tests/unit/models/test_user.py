from sqlalchemy.exc import IntegrityError

from app.enums.account import AccountTypeEnum, AccountFlagEnum, UserPermissionEnum
from app.models.user import User, GlobalUid, UserBindInfo
from config import MerchantEnum
from tests import TestCashierUnitBase


class TestUserModel(TestCashierUnitBase):
    ENABLE_PRINT = False

    def register_user(self, info):
        """
        用户注册
        :param info:
        :return:
        """

        User.register_account(
            info['merchant'],
            info['account'],
            info['ac_type'],
            info['login_pwd'],
        )

        user = User.query_user(info['merchant'], account=info['account'])
        self.assertIsNotNone(user)
        self.assertEqual(user.account, info['account'])
        self.assertEqual(user.ac_type, info['ac_type'])
        return user

    def register_user_not_exist_yet(self, info):
        """
        测试注册不存在的用户
        :param info:
        :return:
        """
        user = User.delete_account(info['merchant'], account=info['account'])
        self.assertIsNone(user)
        self.register_user(info)

    def register_user_already_exist(self, info):
        """
        测试注册不存在的用户
        :param info:
        :return:
        """
        User.delete_account(info['merchant'], account=info['account'])
        self.register_user(info)

        error = None
        try:
            self.register_user(info)
        except IntegrityError as e:
            error = e
        self.assertIsNotNone(error)

    def register_multi_account(self, info):
        """
        测试注册不存在的用户
        :param info:
        :return:
        """
        info['merchant'] = MerchantEnum.TEST
        accounts = [('123456789', 1), ('8888888888', 2), ('9999999999', 3)]
        for account, uid in accounts:
            info['account'] = account
            user = self.register_user(info)
            self.assertEqual(user.uid, uid)
            self.assertEqual(user.account, account)
            merchant = GlobalUid.get_merchant(user.uid)
            self.assertEqual(info['merchant'], merchant)

        info['merchant'] = MerchantEnum.QF3
        accounts = [('123456000', 4), ('88886666888', 5), ('999999888', 6)]
        for account, uid in accounts:
            info['account'] = account
            user = self.register_user(info)
            self.assertEqual(user.uid, uid)
            self.assertEqual(user.account, account)
            merchant = GlobalUid.get_merchant(user.uid)
            self.assertEqual(info['merchant'], merchant)

    def verify_user_login_password(self, info):
        User.delete_account(info['merchant'], account=info['account'])

        self.register_user(info)

        for account in [info['account'], 'xxxx']:
            for merchant in [info['merchant']]:
                for login_pwd in [info['login_pwd'], 'xxxx']:
                    ret = User.verify_login(merchant, account, login_pwd)
                    if info['account'] == account and info['merchant'] == merchant and info['login_pwd'] == login_pwd:
                        self.assertTrue(ret)
                    else:
                        self.assertFalse(ret)

    def query_user(self, info):
        User.delete_account(info['merchant'], account=info['account'])

        self.register_user(info)

        user = User.query_user(info['merchant'], account=info['account'])
        self.assertIsNotNone(user)
        self.assertEqual(user.account, info['account'])
        self.assertEqual(user.ac_type, info['ac_type'])

        user = User.query_user(info['merchant'], uid=user.uid)
        self.assertIsNotNone(user)
        self.assertEqual(user.account, info['account'])
        self.assertEqual(user.ac_type, info['ac_type'])

        try:
            User.query_user(info['merchant'])
        except Exception as e:
            pass
        else:
            self.assert_(False)

        try:
            User.query_user(info['merchant'], uid='xx')
        except Exception as e:
            pass
        else:
            # 期望有异常发生
            self.assert_(False)

    def delete_user(self, info):

        User.delete_account(info['merchant'], account=info['account'])

        self.register_user(info)

        user = User.query_user(info['merchant'], account=info['account'])
        self.assertIsNotNone(user)
        self.assertEqual(user.account, info['account'])
        self.assertEqual(user.merchant, info['merchant'].upper())
        self.assertEqual(user.ac_type, info['ac_type'])

        User.delete_account(info['merchant'], uid=user.uid)

        user = User.query_user(info['merchant'], uid=user.uid)
        self.assertIsNone(user)

    def bind_user(self, merchant, account, name):
        user = User.query_user(merchant, account=account)
        ub = UserBindInfo.bind_account(user.uid, merchant, account, name)

        self.assertEqual(ub.name, name)
        self.assertEqual(ub.merchant, merchant)
        self.assertEqual(ub.account, account)

        ub1 = UserBindInfo.query_bind(merchant, name)
        self.assertEqual(ub.name, ub1.name)
        self.assertEqual(ub.merchant, ub1.merchant)
        self.assertEqual(ub.account, ub1.account)

        UserBindInfo.unbind_account(ub1)
        ub2 = UserBindInfo.query_bind(merchant, name)
        self.assertIsNone(ub2)

    def set_user_flag(self, merchant, account):
        rst = User.update_user_flag(merchant, AccountFlagEnum.VIP, account=account)
        self.assertTrue(rst)
        user = User.query_user(merchant, account=account)
        self.assertEqual(user.flag, AccountFlagEnum.VIP)

    def set_user_permissions(self, merchant, account):

        def check_permissions(_permissions):
            rst = User.update_user_permission(merchant, permissions=_permissions, account=account)
            self.assertTrue(rst)
            user = User.query_user(merchant, account=account)
            print(_permissions, user.permissions)
            self.assertEqual(set([x.name for x in user.permissions]), set([x.name for x in _permissions]))
            print(UserPermissionEnum.join_permissions(_permissions),
                  UserPermissionEnum.join_permissions(user.permissions))
            self.assertEqual(UserPermissionEnum.join_permissions(user.permissions),
                             UserPermissionEnum.join_permissions(_permissions))

        check_permissions([UserPermissionEnum.DEPOSIT])
        check_permissions([UserPermissionEnum.WITHDRAW, UserPermissionEnum.BINDCARD])
        check_permissions([UserPermissionEnum.TRANSFER, UserPermissionEnum.BINDCARD])

    def test_user_model(self):

        info = dict(
            account="+8618977772222",
            merchant=self.t_merchant,
            ac_type=AccountTypeEnum.MOBILE,
            login_pwd="123456789",
            trade_pwd="abcdefg12345",
        )

        self.register_multi_account(info)
        info['account'] = '283283282382'
        self.register_user(info)
        self.register_user_not_exist_yet(info)
        self.register_user_already_exist(info)
        self.verify_user_login_password(info)
        self.query_user(info)
        self.bind_user(info['merchant'], info['account'], '你好大师dfasdfa')
        self.set_user_flag(info['merchant'], info['account'])
        self.set_user_permissions(info['merchant'], info['account'])
