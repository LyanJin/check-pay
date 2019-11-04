from decimal import Decimal

from app.enums.channel import ChannelConfigEnum
from app.enums.trade import InterfaceTypeEnum, OrderStateEnum, PayTypeEnum, OrderSourceEnum, SettleStateEnum, \
    DeliverStateEnum, DeliverTypeEnum
from app.libs.datetime_kit import DateTimeKit
from scripts.order_mix import OrderMixes
from app.logics.order.create_ctl import OrderCreateCtl
from app.logics.order.update_ctl import OrderUpdateCtl
from app.models.channel import ChannelConfig
from app.models.merchant import MerchantFeeConfig
from app.models.order.order import OrderDeposit, OrderWithdraw
from app.models.order.order_detail import OrderDetailDeposit, OrderDetailWithdraw
from app.models.order.order_event import OrderEvent
from config import MerchantEnum
from tests import TestCashierUnitBase


class TestOrderModel(TestCashierUnitBase):
    ENABLE_PRINT = False
    ENABLE_SQL_LOG = False

    def test_order_event_add(self):

        channel_enum = ChannelConfigEnum.CHANNEL_1001

        OrderMixes.add_one_channel_config(channel_enum)

        for merchant in MerchantEnum:
            OrderMixes.add_one_merchant_config(merchant, channel_enum)
            for uid in range(1000, 1005):
                uid += merchant.value
                self.__add_event(uid, merchant, channel_enum, PayTypeEnum.DEPOSIT)
                self.__add_event(uid, merchant, channel_enum, PayTypeEnum.WITHDRAW)

        x = 1

    def test_order_clean_deposit(self):
        # 每天N条数据
        day_num = 3

        uid_range = range(1000, 1005)

        self.__clean_order(PayTypeEnum.WITHDRAW, day_num, uid_range)

    def test_order_clean_withdraw(self):
        # 每天N条数据
        day_num = 3

        uid_range = range(1000, 1005)

        self.__clean_order(PayTypeEnum.WITHDRAW, day_num, uid_range)

    def __clean_order(self, order_type, day_num, uid_range):
        test_order = OrderMixes(order_type)
        test_order.batch_add_orders(day_num, uid_range)

        if order_type == PayTypeEnum.DEPOSIT:
            OrderDeposit.clean_hot_table()
            OrderDetailDeposit.clean_hot_table()
        else:
            OrderWithdraw.clean_hot_table()
            OrderDetailWithdraw.clean_hot_table()

        test_order.check_clean_result(day_num, uid_range)

        test_order.test_one_day_order_clean(day_num, uid_range)
        test_order.check_clean_result(day_num, uid_range)

    def __add_event(self, uid, merchant, channel_enum, order_type):

        order_cls = OrderDeposit if order_type == PayTypeEnum.DEPOSIT else OrderWithdraw

        channel_config = ChannelConfig.query_latest_one(dict(channel_enum=channel_enum))
        merchant_fee_config = MerchantFeeConfig.query_latest_one(dict(
            merchant=merchant,
            payment_way=PayTypeEnum.DEPOSIT,
            payment_method=channel_enum.conf.payment_method,
        ))

        params = dict(
            uid=uid,
            merchant=merchant,
            channel_id=channel_config.channel_id,
            mch_fee_id=merchant_fee_config.config_id,
            source=OrderSourceEnum.TESTING,
            order_type=order_type,
            in_type=InterfaceTypeEnum.CASHIER_H5,
            amount=Decimal("500"),
            comment='谢谢',
            op_account='xxx',
            bank_id=123,
            fee=10 if order_type == PayTypeEnum.WITHDRAW else 0,
        )
        order, ref_id = OrderCreateCtl.create_order_event(**params)
        self.assertIsNotNone(order)

        event = OrderEvent.query_one(dict(ref_id=ref_id), merchant=merchant, date=order.create_time)
        self.assertIsNotNone(event)
        self.assertEqual(order.order_id, event.order_id)
        self.assertEqual(order.uid, event.uid)
        self.assertEqual(ref_id, event.ref_id)

        order = order_cls.query_by_order_id(order_id=event.order_id, merchant=merchant)
        self.assertIsNotNone(order)
        self.assertEqual(params['uid'], order.uid)
        self.assertEqual(params['merchant'], order.merchant)
        self.assertEqual(params['channel_id'], order.channel_id)
        self.assertEqual(params['source'], order.source)
        self.assertEqual(params['amount'], order.amount)
        self.assertTrue(len(order.mch_tx_id) > 0)
        self.assertTrue(len(order.sys_tx_id) > 0)

        # 更新订单
        order, ref_id = OrderUpdateCtl.update_order_event(
            order_id=order.order_id,
            uid=order.uid,
            merchant=merchant,
            state=OrderStateEnum.SUCCESS if order_type == PayTypeEnum.DEPOSIT else OrderStateEnum.ALLOC,
            tx_amount=Decimal("500.32"),
            channel_tx_id='1232283838229929292',
            settle=SettleStateEnum.DONE,
            deliver=DeliverStateEnum.DONE,
            channel_id=channel_config.channel_id,
            mch_fee_id=merchant_fee_config.config_id,
            op_account='xxxx',
            comment='改了改了',
            offer=Decimal('1.22'),
            fee=Decimal('1.22'),
            cost=Decimal('1.22'),
            profit=Decimal('1.22'),
            deliver_type=DeliverTypeEnum.PROXY,
            alloc_time=DateTimeKit.get_cur_datetime(),
            deal_time=DateTimeKit.get_cur_datetime(),
        )
        self.assertIsNotNone(order)

        event = OrderEvent.query_one(dict(ref_id=ref_id), merchant=merchant, date=order.create_time)
        self.assertEqual(order.order_id, event.order_id)
        self.assertEqual(order.uid, event.uid)
        self.assertEqual(ref_id, event.ref_id)

        order3 = order_cls.query_by_order_id(order_id=event.order_id, merchant=merchant)
        self.assertIsNotNone(order3)
        self.assertEqual(params['uid'], order3.uid)
        self.assertEqual(params['merchant'], order3.merchant)
        self.assertEqual(params['channel_id'], order3.channel_id)
        self.assertEqual(params['source'], order3.source)
        self.assertEqual(Decimal("500.32"), order3.tx_amount)
        self.assertEqual(order.order_id, order3.order_id)
        self.assertEqual(order.mch_tx_id, order3.mch_tx_id)
        self.assertEqual(order.sys_tx_id, order3.sys_tx_id)

        order3 = order_cls.query_by_tx_id(tx_id=order.sys_tx_id)
        self.assertIsNotNone(order3)
        self.assertEqual(params['uid'], order3.uid)
        self.assertEqual(params['merchant'], order3.merchant)
        self.assertEqual(params['channel_id'], order3.channel_id)
        self.assertEqual(params['source'], order3.source)
        self.assertEqual(Decimal("500.32"), order3.tx_amount)
        self.assertEqual(order.order_id, order3.order_id)
        self.assertEqual(order.mch_tx_id, order3.mch_tx_id)
        self.assertEqual(order.sys_tx_id, order3.sys_tx_id)

        order3 = order_cls.query_by_uid_someday(merchant=merchant, uid=uid, someday=order.create_time).all()[0]
        self.assertIsNotNone(order3)
        self.assertEqual(params['uid'], order3.uid)
        self.assertEqual(params['merchant'], order3.merchant)
        self.assertEqual(params['channel_id'], order3.channel_id)
        self.assertEqual(params['source'], order3.source)
        self.assertEqual(Decimal("500.32"), order3.tx_amount)
        self.assertEqual(order.order_id, order3.order_id)
        self.assertEqual(order.mch_tx_id, order3.mch_tx_id)
        self.assertEqual(order.sys_tx_id, order3.sys_tx_id)

        begin_time, end_time = DateTimeKit.get_day_begin_end(order.create_time)
        orders = order_cls.query_by_create_time(begin_time, end_time, merchant=merchant, uid=uid).all()
        order3 = orders[-1]
        self.assertIsNotNone(order3)
        self.assertFalse(order3.is_cold_table())
        self.assertEqual(params['uid'], order3.uid)
        self.assertEqual(params['merchant'], order3.merchant)
        self.assertEqual(params['channel_id'], order3.channel_id)
        self.assertEqual(params['source'], order3.source)
        self.assertEqual(Decimal("500.32"), order3.tx_amount)
        self.assertEqual(order.order_id, order3.order_id)
        self.assertEqual(order.mch_tx_id, order3.mch_tx_id)
        self.assertEqual(order.sys_tx_id, order3.sys_tx_id)

        # 冷表查询测试
        begin_time, end_time = DateTimeKit.get_day_begin_end(order.create_time)
        clean_date = order_cls.get_clean_date()
        if clean_date.month == begin_time.month:
            begin_time = clean_date
            orders = order_cls.query_by_create_time(begin_time, end_time, merchant=merchant, uid=uid).all()
            order3 = orders[-1]
            self.assertIsNotNone(order3)
            self.assertTrue(order3.is_cold_table())
            self.assertEqual(params['uid'], order3.uid)
            self.assertEqual(params['merchant'], order3.merchant)
            self.assertEqual(params['channel_id'], order3.channel_id)
            self.assertEqual(params['source'], order3.source)
            self.assertEqual(Decimal("500.32"), order3.tx_amount)
            self.assertEqual(order.order_id, order3.order_id)
            self.assertEqual(order.mch_tx_id, order3.mch_tx_id)
            self.assertEqual(order.sys_tx_id, order3.sys_tx_id)
