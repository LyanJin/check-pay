from decimal import Decimal

from app.logics.transaction.deposit_ctl import DepositTransactionCtl
from scripts.init_data import InitData

if __name__ == '__main__':
    from app.main import flask_app

    def test_withdraw_unit():
        InitData.init_sample_data()

        __test_create_failed()
        __test_deposit_success()
        __test_deposit_fail()

    def __test_create_failed():
        order = InitData.create_one_deposit_order()
        DepositTransactionCtl.order_create_fail(order)

    def __test_deposit_success():
        tx_amount = Decimal('299.99')
        channel_tx_id = '29828239239238298'
        order = InitData.create_one_deposit_order()
        DepositTransactionCtl.success_order_process(order, tx_amount, channel_tx_id)

    def __test_deposit_fail():
        tx_amount = Decimal('299.99')
        channel_tx_id = '29828239239238298'
        order = InitData.create_one_deposit_order()
        DepositTransactionCtl.failed_order_process(order, tx_amount, channel_tx_id)

    with flask_app.app_context():
        test_withdraw_unit()
