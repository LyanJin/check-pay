from scripts.init_data import InitData

if __name__ == '__main__':
    from app.main import flask_app

    with flask_app.app_context():
        for x in range(20):
            InitData.create_one_withdraw_order()
