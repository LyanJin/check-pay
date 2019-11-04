from app.constants.cashier import TRANSACTION_PAGE_SIZE
from app.enums.trade import PayTypeEnum
from app.logics.order.order_list import TransactionListHelper
from scripts.init_data import InitData, DateTimeKit
from tests import TestCashierUnitBase


class ProxyTransactionTest(TestCashierUnitBase):
    """
    代付流程单元测试
    """

    def test_unit_order_list(self):
        InitData.init_sample_data()

        InitData.create_one_refund_order()
        InitData.create_one_transfer_order()
        InitData.create_one_withdraw_order()
        InitData.create_one_deposit_order()

        page_index = 1
        begin_time, end_time = DateTimeKit.get_day_begin_end(DateTimeKit.get_cur_date())
        user = InitData.get_user()

        def get_result(pay_type):
            return TransactionListHelper.get_transaction_list(
                pay_type, user.uid, InitData.merchant, begin_time, end_time, TRANSACTION_PAGE_SIZE,
                page_index
            )

        order_entry_list, order_entry_total = get_result(None)
        self.assertEqual(6, order_entry_total)

        order_entry_list, order_entry_total = get_result(PayTypeEnum.DEPOSIT)
        self.assertEqual(1, order_entry_total)

        order_entry_list, order_entry_total = get_result(PayTypeEnum.WITHDRAW)
        self.assertEqual(2, order_entry_total)
        for item in order_entry_list:
            self.assertIsNotNone(item.get('bank_info'))
            self.assertIsNotNone(item.get('tx_id'))
            self.assertTrue(item['amount'] < 0)

        order_entry_list, order_entry_total = get_result(PayTypeEnum.REFUND)
        self.assertEqual(1, order_entry_total)

        order_entry_list, order_entry_total = get_result(PayTypeEnum.TRANSFER)
        self.assertEqual(1, order_entry_total)
        for item in order_entry_list:
            self.assertIsNotNone(item.get('out_account'))
            self.assertIsNotNone(item.get('in_account'))
            self.assertIsNotNone(item.get('comment'))

        order_entry_list, order_entry_total = get_result(PayTypeEnum.MANUALLY)
        self.assertEqual(1, order_entry_total)

