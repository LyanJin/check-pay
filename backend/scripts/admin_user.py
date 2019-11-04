from app.libs.string_kit import CharOp


def init_admin_user(account, password):
    from app.main import flask_app
    from app.libs.string_kit import RandomString
    from scripts.init_data import InitData

    if not password:
        password = RandomString.gen_random_str(10, (CharOp.N, CharOp.L, CharOp.U))

    with flask_app.app_context():
        InitData.admin_user_account = account
        InitData.password = RandomString.gen_md5_string(password.encode('utf8'))

        admin = InitData.get_admin_user()
        if not admin:
            InitData.init_admin_user()
            admin = InitData.get_admin_user()
            print("account generated, admin: %s, password: %s" % (account, password))
        else:
            admin.reset_password(account=account, login_pwd=InitData.password)
            print("password changed, admin: %s, password: %s" % (account, password))

        rst = admin.verify_login(account, InitData.password)
        print('verify login %s' % rst)

        if rst:
            return account, password

    return None, None


def init_merchant_user(merchant_id, merchant_name, password):
    from app.main import flask_app
    from app.libs.string_kit import RandomString
    if not password:
        password = RandomString.gen_random_str(10, (CharOp.N, CharOp.L, CharOp.U))

    with flask_app.app_context():
        from scripts.init_data import InitData
        InitData.merchant_name = merchant_name
        InitData.merchant_id = merchant_id
        InitData.password = RandomString.gen_md5_string(password.encode('utf8'))

        merchant = InitData.get_merchant_user()
        if not merchant:
            InitData.init_merchant_user()
            merchant = InitData.get_merchant_user()
            print("Merchant generated, merchant: %s, password: %s" % (merchant_name, password))
        else:
            merchant.reset_password(mid=merchant_id, password=InitData.password)
            print("password changed, merchant: %s, password: %s" % (merchant_name, password))

        rst = merchant.verify_login(merchant_name, InitData.password)
        if rst:
            return merchant_name, password
    return None, None


if __name__ == '__main__':
    init_admin_user('kevin2', '')
