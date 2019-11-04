from scripts.init_data import InitData


def init_user(account):
    from app.main import flask_app

    with flask_app.app_context():
        InitData.user_account = account
        InitData.init_user()


if __name__ == '__main__':
    init_user("+8615622153996")
