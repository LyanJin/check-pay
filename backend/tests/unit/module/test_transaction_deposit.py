from decimal import Decimal

from app.logics.transaction.deposit_ctl import DepositTransactionCtl
from scripts.init_data import InitData
from tests import TestCashierUnitBase


class ProxyTransactionTest(TestCashierUnitBase):
    """
    代付流程单元测试
    """

    def test_withdraw_unit(self):
        InitData.init_sample_data()

        self.__test_create_failed()
        self.__test_deposit_success()
        self.__test_deposit_fail()

    def __test_create_failed(self):
        order = InitData.create_one_deposit_order()
        rst = DepositTransactionCtl.order_create_fail(order)
        self.assertTrue(rst)

    def __test_deposit_success(self):
        tx_amount = Decimal('299.99')
        channel_tx_id = '29828239239238298'
        order = InitData.create_one_deposit_order()
        ret = DepositTransactionCtl.success_order_process(order, tx_amount, channel_tx_id)
        self.assertTrue(ret)

    def __test_deposit_fail(self):
        tx_amount = Decimal('299.99')
        channel_tx_id = '29828239239238298'
        order = InitData.create_one_deposit_order()
        DepositTransactionCtl.failed_order_process(order, tx_amount, channel_tx_id)
