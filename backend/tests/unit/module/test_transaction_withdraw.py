from decimal import Decimal

from app.libs.error_code import ResponseSuccess
from app.logics.transaction.withdraw_ctl import WithdrawTransactionCtl
from scripts.init_data import InitData
from tests import TestCashierUnitBase


class ProxyTransactionTest(TestCashierUnitBase):
    """
    代付流程单元测试
    """

    def test_withdraw_unit(self):
        InitData.init_sample_data()

        self.__test_withdraw_success()
        self.__test_withdraw_fail()
        self.__test_manually_withdraw_success()
        self.__test_manually_withdraw_fail()

    def __test_withdraw_success(self):
        amount = tx_amount = Decimal("100.25")
        order = InitData.init_withdraw_order_deal(amount)
        rst = WithdrawTransactionCtl.order_success(order, tx_amount)
        self.assertTrue(rst)

    def __test_withdraw_fail(self):
        amount = Decimal("100.25")
        order = InitData.init_withdraw_order_deal(amount)
        rst = WithdrawTransactionCtl.order_fail(order)
        self.assertTrue(rst)

    def __test_manually_withdraw_success(self):
        amount = Decimal("200.25")
        channel_cost = Decimal('3.5')
        admin_user = InitData.get_admin_user()

        order = InitData.init_withdraw_order_alloc(amount)

        rsp = WithdrawTransactionCtl.manually_withdraw(admin_user, order.merchant, order.order_id)
        self.assertIsInstance(rsp, (ResponseSuccess,))

        # 先成功
        rsp = WithdrawTransactionCtl.manually_withdraw_success(
            admin_user=admin_user,
            merchant=order.merchant,
            order_id=order.order_id,
            channel_cost=channel_cost,
            comment="好贵啊",
        )
        self.assertIsInstance(rsp, (ResponseSuccess,))

        # 后失败
        rsp = WithdrawTransactionCtl.manually_withdraw_failed(
            admin_user=admin_user,
            merchant=order.merchant,
            order_id=order.order_id,
        )
        self.assertIsInstance(rsp, (ResponseSuccess,))

    def __test_manually_withdraw_fail(self):
        amount = Decimal("200.25")
        admin_user = InitData.get_admin_user()

        # 先认领
        order = InitData.init_withdraw_order_alloc(amount)

        # 直接拒绝
        rsp = WithdrawTransactionCtl.manually_withdraw_failed(
            admin_user=admin_user,
            merchant=order.merchant,
            order_id=order.order_id,
        )
        self.assertIsInstance(rsp, (ResponseSuccess,))
