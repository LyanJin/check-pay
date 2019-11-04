from scripts.init_data import InitData


def add_user_balance(account, balance, register=True):
    from app.main import flask_app

    with flask_app.app_context():
        print('alter balance for account: %s, balance: %s' % (account, balance))
        rst, msg = InitData.add_balance_to_user(account, balance, register)
        print('result:', rst, msg)
        if rst == 0:
            print('balance: ', InitData.get_balance(account))
            return InitData.get_balance(account), msg
        else:
            return 0, msg


if __name__ == '__main__':
    add_user_balance('+8618912341234', 500000)
