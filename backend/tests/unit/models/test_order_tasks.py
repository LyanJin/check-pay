from decimal import Decimal

from app.libs.datetime_kit import DateTimeKit
from app.models.order.order_tasks import OrderTasks, OrderTransferLog
from tests import TestBackofficeUnitBase


class TestOrderTasksModel(TestBackofficeUnitBase):
    ENABLE_PRINT = False

    def test_order_tasks(self):
        model = OrderTasks.insert_task(1000)
        models = OrderTasks.query_all()
        self.assertEqual(1, len(models))
        self.assertEqual(model.id, models[0].id)
        self.assertEqual(1000, models[0].order_id)

        model2 = OrderTasks.insert_task(2000)
        models = OrderTasks.query_all()
        self.assertEqual(2, len(models))
        self.assertEqual(model2.id, models[1].id)
        self.assertEqual(2000, models[1].order_id)

        OrderTasks.delete_task(model.id)
        models = OrderTasks.query_all()
        self.assertEqual(1, len(models))

        OrderTasks.delete_task(model2.id)
        models = OrderTasks.query_all()
        self.assertEqual(0, len(models))

    def test_order_transfer_log(self):
        data = dict(
            order_id=1,
            amount=Decimal("199.03"),
            in_account="239814112797121247",
            out_name='张三',
        )

        def check_data(_data, _model):
            self.assertEqual(_data['order_id'], _model.order_id)
            self.assertEqual(_data['amount'], _model.amount)
            self.assertEqual(_data['in_account'], _model.in_account)
            self.assertEqual(_data['out_name'], _model.out_name)

        model = OrderTransferLog.insert_transfer_log(**data)
        self.assertIsNotNone(model)
        check_data(data, model)

        model = OrderTransferLog.query_transfer_log(data['order_id'])
        self.assertIsNotNone(model)
        check_data(data, model)

        data['order_id'] = 1000
        model = OrderTransferLog.insert_transfer_log(**data)
        self.assertIsNotNone(model)
        check_data(data, model)

        model = OrderTransferLog.query_transfer_log(data['order_id'])
        self.assertIsNotNone(model)
        check_data(data, model)

        rst = OrderTransferLog.query_all()
        self.assertEqual(2, len(rst))

        rst = OrderTransferLog.delete_transfer_log_by_date(DateTimeKit.get_cur_date())
        self.assertEqual(2, rst)
        model = OrderTransferLog.query_transfer_log(data['order_id'])
        self.assertIsNone(model)

        rst = OrderTransferLog.query_all()
        self.assertFalse(rst)
