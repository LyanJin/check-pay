from config import MerchantEnum
from scripts.init_data import InitData


def init_data():
    from app.main import flask_app

    with flask_app.app_context():
        InitData.merchant = MerchantEnum.TEST_API
        InitData.init_sample_data()


if __name__ == '__main__':
    init_data()
