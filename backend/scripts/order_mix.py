import random
from decimal import Decimal

from app.enums.channel import ChannelConfigEnum, ChannelStateEnum
from app.enums.trade import PayTypeEnum, InterfaceTypeEnum, PayTypeEnum, PaymentFeeTypeEnum, SettleTypeEnum, \
    OrderSourceEnum
from app.libs.datetime_kit import DateTimeKit, DateTimeFormatEnum
from app.logics.order.create_ctl import OrderCreateCtl
from app.models.channel import ChannelConfig
from app.models.merchant import MerchantFeeConfig
from app.models.order.order import OrderDeposit, OrderWithdraw
from config import MerchantEnum


class OrderMixes:
    order_cls = None

    def __init__(self, order_type):
        self.order_type = order_type

        if order_type == PayTypeEnum.DEPOSIT:
            self.order_cls = OrderDeposit
        else:
            self.order_cls = OrderWithdraw

    @classmethod
    def add_one_channel_config(cls, channel_enum):
        channel1 = dict(
            fee=Decimal("1.8"),
            fee_type=PaymentFeeTypeEnum.PERCENT_PER_ORDER,
            limit_per_min=500,
            limit_per_max=30000,
            limit_day_max=50000,
            trade_begin_hour=12,
            trade_begin_minute=0,
            trade_end_hour=23,
            trade_end_minute=30,
            maintain_begin=DateTimeKit.str_to_datetime("2019-09-27 09:00:00", DateTimeFormatEnum.SECONDS_FORMAT),
            maintain_end=DateTimeKit.str_to_datetime("2025-12-20 23:00:00", DateTimeFormatEnum.SECONDS_FORMAT),
            state=ChannelStateEnum.TESTING,
            settlement_type=SettleTypeEnum.D0,
            priority=channel_enum.value,
        )
        ChannelConfig.update_channel(channel_enum, **channel1)

    @classmethod
    def add_one_merchant_config(cls, merchant, channel_enum, payment_way=PayTypeEnum.DEPOSIT):
        params = [
            dict(
                merchant=merchant,
                payment_way=payment_way,
                payment_method=channel_enum.conf.payment_method,
                fee_type=PaymentFeeTypeEnum.PERCENT_PER_ORDER,
                value=Decimal("1.22"),
            ),
        ]
        MerchantFeeConfig.update_fee_config(merchant, params)

    def batch_add_orders_no_check(self, day_num, uid_range):
        clean_date = DateTimeKit.to_datetime(self.order_cls.get_clean_date())
        end_time = clean_date + DateTimeKit.time_delta(days=self.order_cls.HOT_DAYS + 1)  # +1 包含今天

        days = (end_time - clean_date).days

        print('clean_date: %s, end_time: %s, days: %s, day_num: %s, uid_range: %s' % (
            clean_date, end_time, days, day_num, uid_range))

        channel_enum = ChannelConfigEnum.CHANNEL_1001

        self.add_one_channel_config(channel_enum)

        for merchant in MerchantEnum:

            self.add_one_merchant_config(merchant, channel_enum)

            for uid in uid_range:
                for create_time in DateTimeKit.gen_date_range(clean_date, days):
                    # 每天多少条数据
                    for x in range(day_num):
                        self.create_one_order(merchant, uid, create_time, channel_enum)

                begin_time = clean_date
                if begin_time.month == end_time.month:
                    c = self.order_cls.query_by_create_time(
                        begin_time,
                        end_time,
                        merchant=merchant, uid=uid
                    ).count()

                    print('total hot orders: %s, merchant: %s, uid: %s' % (c, merchant, uid))

                begin_time = clean_date
                if begin_time.month == end_time.month:
                    c = self.order_cls.query_by_create_time(
                        begin_time,
                        end_time,
                        merchant=merchant, uid=uid, only_cold=True
                    ).count()

                    print('total cold orders: %s, merchant: %s, uid: %s' % (c, merchant, uid))

    def create_one_order(self, merchant, uid, create_time, channel_enum):
        channel_config = ChannelConfig.query_latest_one(dict(channel_enum=channel_enum))
        merchant_fee_config = MerchantFeeConfig.query_latest_one(dict(
            merchant=merchant,
            payment_way=PayTypeEnum.DEPOSIT,
            payment_method=channel_enum.conf.payment_method,
        ))
        params = dict(
            uid=uid,
            merchant=merchant,
            source=OrderSourceEnum.TESTING,
            order_type=self.order_type,
            channel_id=channel_config.channel_id,
            mch_fee_id=merchant_fee_config.config_id,
            create_time=create_time + DateTimeKit.time_delta(
                hours=random.randint(0, 23),
                # hours=random.choice([0, 23]),
                minutes=random.randint(0, 59),
                seconds=random.randint(0, 59),
            ),
            in_type=InterfaceTypeEnum.CASHIER_H5,
            amount=Decimal("500.23"),
            bank_id=123,
            pay_method=channel_config.channel_enum.conf['payment_method'],
            fee=10 if self.order_type == PayTypeEnum.WITHDRAW else 0,
        )
        # print(params['create_time'])
        order = OrderCreateCtl.create_order_event(**params)
        assert order

    def batch_add_orders(self, day_num, uid_range):
        clean_date = DateTimeKit.to_datetime(self.order_cls.get_clean_date())
        end_time = clean_date + DateTimeKit.time_delta(days=self.order_cls.HOT_DAYS + 1)  # +1 包含今天

        days = (end_time - clean_date).days

        print('clean_date: %s, end_time: %s, days: %s, day_num: %s, uid_range: %s' % (
            clean_date, end_time, days, day_num, uid_range))

        channel_enum = ChannelConfigEnum.CHANNEL_1001

        self.add_one_channel_config(channel_enum)

        for merchant in MerchantEnum:

            self.add_one_merchant_config(merchant, channel_enum)

            for uid in uid_range:

                last_time = None

                for create_time in DateTimeKit.gen_date_range(clean_date, days):
                    # 每天多少条数据
                    for x in range(day_num):
                        self.create_one_order(merchant, uid, create_time, channel_enum)

                    c = self.order_cls.query_by_uid_someday(merchant, uid, create_time).count()
                    assert day_num == c, 'day_num: %s, c: %s' % (day_num, c)

                    c = self.order_cls.query_by_uid_someday(merchant, uid, create_time, only_cold=True).count()
                    assert day_num == c, 'day_num: %s, c: %s' % (day_num, c)

                    last_time = create_time

                assert end_time == last_time + DateTimeKit.time_delta(days=1)
                print('generated %s orders for user %s' % (day_num * days, uid))

            day_count = day_num * (days - 1) * len(uid_range)
            begin_time = clean_date + DateTimeKit.time_delta(days=1)
            if begin_time.month == end_time.month:
                c = self.order_cls.query_by_create_time(
                    begin_time,
                    end_time,
                    merchant=merchant, date=clean_date
                ).count()
                assert day_count == c, 'day_count: %s, c: %s' % (day_count, c)
                print('total hot orders %s for merchant %s' % (day_count, merchant))

            day_count = day_num * days * len(uid_range)
            begin_time = clean_date
            if begin_time.month == end_time.month:
                c = self.order_cls.query_by_create_time(
                    begin_time,
                    end_time,
                    merchant=merchant, date=clean_date
                ).count()
                assert day_count == c, 'day_count: %s, c: %s' % (day_count, c)
                print('total cold orders %s for merchant %s' % (day_count, merchant))

    def check_clean_result(self, day_num, uid_range):
        """
        检查清理后的当天数据是否为空，活跃数据是否正常，备份数据是否正常
        :param day_num:
        :param uid_range:
        :return:
        """
        clean_date = DateTimeKit.to_datetime(self.order_cls.get_clean_date())
        end_time = clean_date + DateTimeKit.time_delta(days=self.order_cls.HOT_DAYS + 1)  # +1 包含今天

        days = (end_time - clean_date).days

        print('check, clean_date: %s, end_time: %s, days: %s, day_num: %s, uid_range: %s' % (
            clean_date, end_time, days, day_num, uid_range))

        for merchant in MerchantEnum:
            for uid in uid_range:
                last_time = None
                for create_time in DateTimeKit.gen_date_range(clean_date, days):
                    c = self.order_cls.query_by_uid_someday(merchant, uid, create_time, only_hot=True).count()
                    if create_time == clean_date:
                        # 当天热数据没有了
                        assert 0 == c, 'day_num: %s, c: %s' % (0, c)
                    else:
                        assert day_num == c, 'day_num: %s, c: %s' % (day_num, c)

                    c = self.order_cls.query_by_uid_someday(merchant, uid, create_time, only_cold=True).count()
                    assert day_num == c, 'day_num: %s, c: %s' % (day_num, c)

                    last_time = create_time

                assert end_time == last_time + DateTimeKit.time_delta(days=1)

            # 热数据少一天的数据
            day_count = day_num * (days - 1) * len(uid_range)
            begin_time = clean_date + DateTimeKit.time_delta(days=1)
            if begin_time.month == end_time.month:
                c = self.order_cls.query_by_create_time(
                    begin_time,
                    end_time,
                    merchant=merchant, date=clean_date
                ).count()
                assert day_count == c, 'day_count: %s, c: %s' % (day_count, c)
                print('after clean, hot orders count: %s, merchant: %s' % (day_count, merchant))

            # 冷表数据不变
            day_count = day_num * days * len(uid_range)
            begin_time = clean_date
            if begin_time.month == end_time.month:
                c = self.order_cls.query_by_create_time(
                    begin_time,
                    end_time,
                    merchant=merchant, date=clean_date
                ).count()
                assert day_count == c, 'day_count: %s, c: %s' % (day_count, c)
                print('after clean, cold orders count: %s, merchant: %s' % (day_count, merchant))

    def test_one_day_order_clean(self, day_num, uid_range):
        clean_date = DateTimeKit.to_datetime(self.order_cls.get_clean_date())
        someday = clean_date - DateTimeKit.time_delta(days=2)

        channel_enum = ChannelConfigEnum.CHANNEL_1001

        self.add_one_channel_config(channel_enum)

        for merchant in MerchantEnum:
            self.add_one_merchant_config(merchant, channel_enum)

            for uid in uid_range:

                for x in range(day_num):
                    self.create_one_order(merchant, uid, someday, channel_enum)

                c = self.order_cls.query_by_uid_someday(merchant, uid, someday).count()
                assert day_num == c, 'day_num: %s, c: %s' % (day_num, c)
                c = self.order_cls.query_by_uid_someday(merchant, uid, someday, only_cold=True).count()
                assert day_num == c, 'day_num: %s, c: %s' % (day_num, c)

        self.order_cls.clean_hot_table(seconds=0.1, clean_date=someday)

        for merchant in MerchantEnum:
            for uid in uid_range:
                c = self.order_cls.query_by_uid_someday(merchant, uid, someday, only_hot=True).count()
                assert 0 == c, 'day_num: %s, c: %s' % (0, c)
                c = self.order_cls.query_by_uid_someday(merchant, uid, someday, only_cold=True).count()
                assert day_num == c, 'day_num: %s, c: %s' % (day_num, c)
