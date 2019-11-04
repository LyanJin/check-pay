from decimal import Decimal

from app.enums.channel import ChannelConfigEnum
from app.enums.trade import SettleTypeEnum, PaymentFeeTypeEnum, InterfaceTypeEnum, PayMethodEnum, PaymentTypeEnum
from app.libs.datetime_kit import DateTimeKit, DateTimeFormatEnum
from app.logics.channel.channel_list import ChannelListHelper
from app.models.channel import ChannelConfig, ProxyChannelConfig, ChannelRouter, ChannelRouter2
from config import MerchantEnum
from tests import TestBackofficeUnitBase


class TestChannelConfigModel(TestBackofficeUnitBase):
    ENABLE_PRINT = False
    ENABLE_SQL_LOG = False

    def test_channel_config_model(self):
        data = dict(
            channel_enum=ChannelConfigEnum.CHANNEL_1001,
            fee=Decimal("2.1"),
            fee_type=PaymentFeeTypeEnum.PERCENT_PER_ORDER,
            limit_per_min=Decimal("100.0"),
            limit_per_max=Decimal("1000.0"),
            limit_day_max=Decimal("500000.0"),
            trade_begin_hour=9,
            trade_begin_minute=0,
            trade_end_hour=20,
            trade_end_minute=30,
            settlement_type=SettleTypeEnum.D0,
            maintain_begin=DateTimeKit.str_to_datetime("2016-10-01 09:30", DateTimeFormatEnum.MINUTES_FORMAT),
            maintain_end=DateTimeKit.str_to_datetime("2016-10-02 21:30", DateTimeFormatEnum.MINUTES_FORMAT),
            priority=1
        )

        self.__update_channel(data, 1, 1)

        data['fee'] = Decimal("3.55")
        data['priority'] = 10
        data['maintain_begin'] = DateTimeKit.str_to_datetime("2016-10-01 12:30", DateTimeFormatEnum.MINUTES_FORMAT)
        self.__update_channel(data, 1, 2)

        data['priority'] = -100
        data['channel_enum'] = ChannelConfigEnum.CHANNEL_1002
        self.__update_channel(data, 2, 3)

    def __update_channel(self, data, latest, count):
        ChannelConfig.update_channel(**data)

        channels = ChannelConfig.query_all()
        self.assertEqual(count, len(channels))

        all_configs = list(ChannelConfig.filter_latest_items(channels))
        self.assertEqual(latest, len(all_configs))

        # channel_config = all_configs[0]

        # for k, v in data.items():
        #     self.assertEqual(data[k], getattr(channel_config, k))


class TestProxyChannelConfigModel(TestBackofficeUnitBase):
    ENABLE_PRINT = False
    ENABLE_SQL_LOG = False

    def test_channel_config_model(self):
        data = dict(
            channel_enum=ChannelConfigEnum.CHANNEL_1001,
            fee=Decimal("2.1"),
            fee_type=PaymentFeeTypeEnum.YUAN_PER_ORDER,
            limit_per_min=Decimal("100.0"),
            limit_per_max=Decimal("1000.0"),
            limit_day_max=Decimal("500000.0"),
            trade_begin_hour=9,
            trade_begin_minute=0,
            trade_end_hour=20,
            trade_end_minute=30,
            maintain_begin=DateTimeKit.str_to_datetime("2016-10-01 09:30", DateTimeFormatEnum.MINUTES_FORMAT),
            maintain_end=DateTimeKit.str_to_datetime("2016-10-02 21:30", DateTimeFormatEnum.MINUTES_FORMAT),
        )

        self.__update_channel(data, 1, 1)

        data['fee'] = Decimal("3.55")
        data['maintain_begin'] = DateTimeKit.str_to_datetime("2016-10-01 12:30", DateTimeFormatEnum.MINUTES_FORMAT)
        self.__update_channel(data, 1, 2)

        data['channel_enum'] = ChannelConfigEnum.CHANNEL_1002
        self.__update_channel(data, 2, 3)

    def __update_channel(self, data, latest, count):
        ProxyChannelConfig.update_channel(**data)

        channels = list(ProxyChannelConfig.query_all())
        self.assertEqual(count, len(channels))

        all_configs = list(ProxyChannelConfig.filter_latest_items(channels))
        self.assertEqual(latest, len(all_configs))

        # channel_config = all_configs[count - 1]

        # for k, v in data.items():
        #     self.assertEqual(data[k], getattr(channel_config, k))


class TestChannelRouter(TestBackofficeUnitBase):
    def test_channel_guid_rule(self):
        data = dict(
            config_list=[
                dict(payment_type=PaymentTypeEnum.ZHIFUBAO, priority=100),
                dict(payment_type=PaymentTypeEnum.WEIXIN, priority=200),
                dict(payment_type=PaymentTypeEnum.YINLIAN, priority=10),
                dict(payment_type=PaymentTypeEnum.YUNSHANFU, priority=50),
            ],
            amount_min=Decimal('100.33'),
            amount_max=Decimal('500.22'),
            interface=InterfaceTypeEnum.CASHIER_H5,
            merchants=[MerchantEnum.TEST, MerchantEnum.QF2],
            uid_list=[1, 2, 3, 4],
        )
        rule = ChannelRouter.create_rule(**data)

        def check_item_and_data(_data, _item):
            self.assertEqual(set([x.name for x in _data['merchants']]), set([x.name for x in _item.merchants]))
            self.assertEqual(set(_data['uid_list']), set(_item.uid_list))
            self.assertEqual(_data['interface'], _item.interface)
            self.assertEqual(len(_data['config_list']), len(_item.config_list))

        check_item_and_data(data, rule)

        count = 1
        all_configs = list(ChannelRouter.query_all())
        self.assertEqual(count, len(all_configs))
        q_rule = all_configs[count - 1]
        self.assertEqual(rule.router_id, q_rule.router_id)

        data = dict(
            router_id=q_rule.router_id,
            config_list=[
                dict(payment_type=PaymentTypeEnum.ZHIFUBAO, priority=100),
                dict(payment_type=PaymentTypeEnum.WEIXIN, priority=200),
                dict(payment_type=PaymentTypeEnum.YUNSHANFU, priority=50),
            ],
            amount_min=Decimal('800.33'),
            amount_max=Decimal('3000.22'),
            interface=InterfaceTypeEnum.CASHIER_H5,
            merchants=[MerchantEnum.TEST, MerchantEnum.QF3],
            uid_list=[1, 3, 4],
        )
        rule, error = ChannelRouter.update_rule(**data)
        check_item_and_data(data, rule)

        data['uid_list'] = [10, 20, 30]
        data.pop('router_id')
        data['config_list'] = [
            dict(payment_type=PaymentTypeEnum.ZHIFUBAO, priority=100),
            dict(payment_type=PaymentTypeEnum.WEIXIN, priority=200),
            dict(payment_type=PaymentTypeEnum.YINLIAN, priority=10),
            dict(payment_type=PaymentTypeEnum.YUNSHANFU, priority=50),
        ]
        rule = ChannelRouter.create_rule(**data)
        check_item_and_data(data, rule)

        data['amount_min'] = Decimal('400')
        data['amount_max'] = Decimal('500')
        data['interface'] = InterfaceTypeEnum.API
        data['merchants'] = []
        data['uid_list'] = []
        data['config_list'] = [
            dict(payment_type=PaymentTypeEnum.YINLIAN, priority=10),
            dict(payment_type=PaymentTypeEnum.YUNSHANFU, priority=50),
        ]
        rule = ChannelRouter.create_rule(**data)
        check_item_and_data(data, rule)

        data['amount_min'] = 0
        data['amount_max'] = 0
        data['interface'] = InterfaceTypeEnum.CASHIER_PC
        data['merchants'] = []
        data['uid_list'] = []
        data['config_list'] = [
            dict(payment_type=PaymentTypeEnum.YINLIAN, priority=4),
            dict(payment_type=PaymentTypeEnum.YUNSHANFU, priority=8),
            dict(payment_type=PaymentTypeEnum.ZHIFUBAO, priority=3),
            dict(payment_type=PaymentTypeEnum.WEIXIN, priority=5),
            dict(payment_type=PaymentTypeEnum.BANKCARD, priority=10),
            dict(payment_type=PaymentTypeEnum.JDQIANBAO, priority=7),
        ]
        rule = ChannelRouter.create_rule(**data)
        check_item_and_data(data, rule)

        data['interface'] = None
        data['config_list'] = [
            dict(payment_type=PaymentTypeEnum.YINLIAN, priority=4),
            dict(payment_type=PaymentTypeEnum.ZHIFUBAO, priority=3),
            dict(payment_type=PaymentTypeEnum.WEIXIN, priority=5),
            dict(payment_type=PaymentTypeEnum.BANKCARD, priority=10),
            dict(payment_type=PaymentTypeEnum.JDQIANBAO, priority=7),
        ]
        rule = ChannelRouter.create_rule(**data)
        check_item_and_data(data, rule)

        count = 5
        all_configs = list(ChannelRouter.query_all())
        self.assertEqual(count, len(all_configs))
        q_rule = all_configs[count - 1]
        self.assertEqual(rule.router_id, q_rule.router_id)

        config_list = ChannelListHelper.get_channel_payment_type_router(uid=3, amount=Decimal("1000"),
                                                                        merchant=MerchantEnum.QF3,
                                                                        interface=InterfaceTypeEnum.CASHIER_H5)
        print('config_list', config_list)
        self.assertEqual(3, len(config_list))

        config_list = ChannelListHelper.get_channel_payment_type_router(uid=20, amount=Decimal("1000"),
                                                                        merchant=MerchantEnum.QF3,
                                                                        interface=InterfaceTypeEnum.CASHIER_H5)
        print('config_list', config_list)
        self.assertEqual(4, len(config_list))

        config_list = ChannelListHelper.get_channel_payment_type_router(amount=Decimal("450"),
                                                                        interface=InterfaceTypeEnum.API)
        print('config_list', config_list)
        self.assertEqual(2, len(config_list))

        config_list = ChannelListHelper.get_channel_payment_type_router(interface=InterfaceTypeEnum.CASHIER_PC)
        print('config_list', config_list)
        self.assertEqual(6, len(config_list))

        config_list = ChannelListHelper.get_channel_payment_type_router()
        print('config_list', config_list)
        self.assertEqual(5, len(config_list))

        config_list = ChannelListHelper.get_channel_payment_type_router(interface=InterfaceTypeEnum.API)
        print('config_list', config_list)
        self.assertEqual(5, len(config_list))


class TestChannelRouter2(TestBackofficeUnitBase):
    def test_channel_router2(self):
        data = dict(
            channel_enum=ChannelConfigEnum.CHANNEL_7001,
            amount_min=Decimal('100.33'),
            amount_max=Decimal('500.22'),
            interface=InterfaceTypeEnum.CASHIER_H5,
            merchants=[MerchantEnum.TEST, MerchantEnum.QF2],
            uid_list=[1, 2, 3, 4],
        )
        rule, msg = ChannelRouter2.update_router(**data)

        def check_item_and_data(_data, _item):
            self.assertEqual(set([x.name for x in _data['merchants']]), set([x.name for x in _item.merchants]))
            self.assertEqual(set(_data['uid_list']), set(_item.uid_list))
            self.assertEqual(_data['interface'].name, _item.interface.name)
            self.assertEqual(_data['channel_enum'], _item.channel_enum)
            self.assertEqual(_data['amount_min'], _item.amount_min)
            self.assertEqual(_data['amount_max'], _item.amount_max)

        check_item_and_data(data, rule)

        count = 1
        all_configs = list(ChannelRouter2.query_all())
        self.assertEqual(count, len(all_configs))
        q_rule = all_configs[count - 1]
        self.assertEqual(rule.router_id, q_rule.router_id)

        data['amount_min'] = Decimal('800')
        data['amount_max'] = Decimal('3000')
        data['interface'] = InterfaceTypeEnum.CASHIER_H5
        data['merchants'] = [MerchantEnum.TEST, MerchantEnum.QF3]
        data['uid_list'] = [1, 3, 4]
        rule, msg = ChannelRouter2.update_router(**data)
        check_item_and_data(data, rule)

        data['uid_list'] = [10, 20, 30]
        data['channel_enum'] = ChannelConfigEnum.CHANNEL_2003
        rule, msg = ChannelRouter2.update_router(**data)
        check_item_and_data(data, rule)

        data['amount_min'] = Decimal('400')
        data['amount_max'] = Decimal('500')
        data['interface'] = InterfaceTypeEnum.API
        data['merchants'] = []
        data['uid_list'] = []
        data['channel_enum'] = ChannelConfigEnum.CHANNEL_3001
        rule, msg = ChannelRouter2.update_router(**data)
        check_item_and_data(data, rule)

        data['amount_min'] = 0
        data['amount_max'] = 0
        data['interface'] = InterfaceTypeEnum.CASHIER_PC
        data['merchants'] = []
        data['uid_list'] = []
        data['channel_enum'] = ChannelConfigEnum.CHANNEL_4003
        rule, msg = ChannelRouter2.update_router(**data)
        check_item_and_data(data, rule)

        count = 4
        all_configs = list(ChannelRouter2.query_all())
        self.assertEqual(count, len(all_configs))
        q_rule = all_configs[count - 1]
        self.assertEqual(rule.router_id, q_rule.router_id)

        router = ChannelRouter2.get_one_match_router(all_configs, uid=3, amount=Decimal("1000"),
                                                     merchant=MerchantEnum.QF3,
                                                     interface=InterfaceTypeEnum.CASHIER_H5)
        print('channel', router.channel_enum)
        self.assertEqual(ChannelConfigEnum.CHANNEL_7001, router.channel_enum)

        router = ChannelRouter2.get_one_match_router(all_configs, uid=20, amount=Decimal("1000"),
                                                     merchant=MerchantEnum.QF3,
                                                     interface=InterfaceTypeEnum.CASHIER_H5)
        print('channel', router.channel_enum)
        self.assertEqual(ChannelConfigEnum.CHANNEL_2003, router.channel_enum)

        router = ChannelRouter2.get_one_match_router(all_configs, interface=InterfaceTypeEnum.CASHIER_PC)
        print('channel', router.channel_enum)
        self.assertEqual(ChannelConfigEnum.CHANNEL_4003, router.channel_enum)

        router = ChannelRouter2.get_one_match_router(all_configs, amount=Decimal("450"),
                                                     interface=InterfaceTypeEnum.API)
        print('channel', router.channel_enum)
        self.assertEqual(ChannelConfigEnum.CHANNEL_3001, router.channel_enum)

        router = ChannelRouter2.get_one_match_router(all_configs)
        self.assertEqual(None, router)
