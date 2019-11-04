import copy
import hashlib
import random
from decimal import Decimal

from app.enums.account import AccountStateEnum
from app.libs.datetime_kit import DateTimeKit
from app.libs.error_code import SqlIntegrityError
from app.libs.order_kit import OrderUtils
from app.libs.string_kit import RandomString
from config import MerchantTypeEnum
from app.enums.trade import PayTypeEnum, BalanceTypeEnum, BalanceAdjustTypeEnum, PayMethodEnum, \
    PaymentFeeTypeEnum, PayTypeEnum, OrderSourceEnum
from app.models.merchant import MerchantInfo, MerchantBalanceEvent, MerchantFeeConfig
from config import MerchantEnum
from tests import TestBackofficeUnitBase


class TestMerchantFeeConfig(TestBackofficeUnitBase):
    ENABLE_SQL_LOG = False

    def check_result(self, conf_dict):
        payment_method = conf_dict.get('payment_method')
        conf = MerchantFeeConfig.query_latest_one(query_fields=dict(
            merchant=conf_dict['merchant'],
            payment_way=conf_dict['payment_way'],
            payment_method=payment_method
        ))
        self.assertIsNotNone(conf)
        self.assertEqual(conf_dict['merchant'], conf['merchant'])
        if payment_method:
            self.assertEqual(conf_dict['payment_method'], conf['payment_method'])
        self.assertEqual(conf_dict['fee_type'], conf['fee_type'])
        self.assertEqual(conf_dict['value'], conf['value'])

    def add_one_config(self, merchant, params):
        MerchantFeeConfig.update_fee_config(merchant, params)
        for conf_dict in params:
            self.check_result(conf_dict)

    def test_merchant_fee_config_model(self):
        # 添加测试
        count = 0
        latest_count = 0
        for merchant in MerchantEnum:
            for payment_way in PayTypeEnum:
                if payment_way == PayTypeEnum.DEPOSIT:
                    for payment_method in PayMethodEnum:
                        for fee_type in PaymentFeeTypeEnum:
                            params = [
                                dict(
                                    merchant=merchant,
                                    payment_way=payment_way,
                                    payment_method=payment_method,
                                    fee_type=fee_type,
                                    value=Decimal("1.22"),
                                ),
                            ]
                            self.add_one_config(merchant, params)
                            count += 1
                        latest_count += 1
                else:
                    for fee_type in PaymentFeeTypeEnum:
                        params = [
                            dict(
                                merchant=merchant,
                                payment_way=payment_way,
                                fee_type=fee_type,
                                value=Decimal("3.22"),
                            ),
                        ]
                        self.add_one_config(merchant, params)
                        count += 1
                    latest_count += 1

        all_configs = MerchantFeeConfig.query_all()
        add_num = len(list(all_configs))
        self.assertEqual(count, add_num)

        latest_configs = MerchantFeeConfig.filter_latest_items(all_configs)
        x_latest_count = len(list(latest_configs))
        self.assertEqual(len(MerchantEnum.get_names()), x_latest_count)

        # 修改测试
        count = 0
        for merchant in MerchantEnum:
            for payment_way in PayTypeEnum:
                if payment_way == PayTypeEnum.DEPOSIT:
                    for payment_method in PayMethodEnum:
                        for fee_type in PaymentFeeTypeEnum:
                            params = [
                                dict(
                                    merchant=merchant,
                                    payment_way=payment_way,
                                    payment_method=payment_method,
                                    fee_type=fee_type,
                                    value=Decimal("1.33"),
                                ),
                            ]
                            self.add_one_config(merchant, params)
                            count += 1
                else:
                    for fee_type in PaymentFeeTypeEnum:
                        params = [
                            dict(
                                merchant=merchant,
                                payment_way=payment_way,
                                fee_type=fee_type,
                                value=Decimal("2.33"),
                            ),
                        ]
                        self.add_one_config(merchant, params)
                        count += 1

        add_num += count

        # 更新不会增加条目
        all_configs = MerchantFeeConfig.query_all()
        num = len(list(all_configs))
        self.assertEqual(add_num, num)

        latest_configs = MerchantFeeConfig.filter_latest_items(all_configs)
        x_latest_count = len(list(latest_configs))
        self.assertEqual(len(MerchantEnum.get_names()), x_latest_count)

        # 批量修改测试
        count = 0
        valid_count = 0
        for merchant in MerchantEnum:
            params = []
            for payment_way in PayTypeEnum:
                if payment_way == PayTypeEnum.DEPOSIT:
                    for payment_method in PayMethodEnum:
                        params.append(dict(
                            merchant=merchant,
                            payment_way=payment_way,
                            payment_method=payment_method,
                            fee_type=PaymentFeeTypeEnum.PERCENT_PER_ORDER,
                            value=Decimal("1.22"),
                        ))
                        count += 1
                else:
                    params.append(dict(
                        merchant=merchant,
                        payment_way=payment_way,
                        fee_type=PaymentFeeTypeEnum.PERCENT_PER_ORDER,
                        value=Decimal("3.22"),
                    ))
                    count += 1

            valid_count += len(params)
            self.add_one_config(merchant, params)

        add_num += count

        all_configs = MerchantFeeConfig.query_all()
        num = len(list(all_configs))
        self.assertEqual(add_num, num)

        latest_configs = MerchantFeeConfig.filter_latest_items(all_configs)
        x_latest_count = len(list(latest_configs))
        self.assertEqual(valid_count, x_latest_count)

        MerchantFeeConfig.delete_all()
        num = len(list(MerchantFeeConfig.query_all()))
        self.assertEqual(0, num)


class TestMerchantBalanceModel(TestBackofficeUnitBase):
    ENABLE_PRINT = False
    ENABLE_SQL_LOG = False

    def test_merchant_model(self):
        self.__create_merchant_info()
        self.__check_add_event_params_error()
        self.__add_event()
        MerchantInfo.delete_all()

    def __change_balance(self, data: dict, result: int, balance_check: dict, event_check: dict):
        """
        修改
        :param data:
        :param result:merchant_balance_event_test_91
        :param balance_check:
        :param event_check:
        :return:
        """
        # 修改余额
        data = copy.deepcopy(data)
        ref_id = OrderUtils.gen_unique_ref_id()
        data['ref_id'] = ref_id
        event_check['tx_id'] = data['tx_id'] = OrderUtils.gen_normal_tx_id(int(data['value']))

        rst, msg = MerchantBalanceEvent.update_balance(**data)
        self.assertEqual(result, rst)

        if rst == 0:
            event_check['ref_id'] = ref_id

        # 验证余额
        merchant = MerchantInfo.query_merchant(data['merchant'])
        self.assertIsNotNone(merchant)
        balance_total = sum(balance_check.values())
        self.assertEqual(balance_total, merchant.balance_total)
        self.assertEqual(balance_check['balance_available'], merchant.balance_available)
        self.assertEqual(balance_check['balance_frozen'], merchant.balance_frozen)
        self.assertEqual(balance_check['balance_income'], merchant.balance_income)

        if rst != 0:
            # 更新失败，就不用验证结果事件了
            return rst

        event = MerchantBalanceEvent.query_event(merchant=merchant.merchant,
                                                 create_time=DateTimeKit.get_cur_datetime(),
                                                 ref_id=ref_id).first()
        value = event_check['value']
        if event_check['ad_type'] == BalanceAdjustTypeEnum.MINUS:
            # 做减法
            value = -event_check['value']

        self.assertEqual(event_check['merchant'], event.merchant)
        self.assertEqual(event_check['source'], event.source)
        self.assertEqual(event_check['bl_type'], event.bl_type)
        self.assertEqual(event_check['ad_type'], event.ad_type)
        self.assertEqual(value, event.value_real)
        self.assertEqual(event_check['tx_id'], event.tx_id)
        self.assertEqual(event_check['comment'], event.comment)
        self.assertEqual(event_check['ref_id'], event.ref_id)

        return rst

    def __check_add_event_params_error(self):
        ###########################################################
        # 余额修改,参数错误
        ###########################################################

        ref_id = hashlib.md5('lakjdflasjfadl;kfja'.encode('utf8')).hexdigest()

        # value是0
        rst, msg = MerchantBalanceEvent.update_balance(
            merchant=MerchantEnum.TEST,
            ref_id=ref_id,
            source=OrderSourceEnum.TESTING,
            order_type=PayTypeEnum.DEPOSIT,
            bl_type=BalanceTypeEnum.AVAILABLE,
            ad_type=BalanceAdjustTypeEnum.PLUS,
            tx_id=OrderUtils.gen_normal_tx_id(100),
            value=0,
        )
        self.assertEqual(rst, -1)

        # value是负数
        rst, msg = MerchantBalanceEvent.update_balance(
            merchant=MerchantEnum.TEST,
            ref_id=ref_id,
            source=OrderSourceEnum.TESTING,
            order_type=PayTypeEnum.DEPOSIT,
            bl_type=BalanceTypeEnum.AVAILABLE,
            ad_type=BalanceAdjustTypeEnum.PLUS,
            tx_id=OrderUtils.gen_normal_tx_id(100),
            value=-1.0,
        )
        self.assertEqual(rst, -1)

        # 提款不能用加法
        rst, msg = MerchantBalanceEvent.update_balance(
            merchant=MerchantEnum.TEST,
            ref_id=ref_id,
            bl_type=BalanceTypeEnum.AVAILABLE,
            source=OrderSourceEnum.TESTING,
            order_type=PayTypeEnum.WITHDRAW,
            ad_type=BalanceAdjustTypeEnum.PLUS,
            value=120.00,
            tx_id=OrderUtils.gen_normal_tx_id(100),
        )
        self.assertEqual(rst, -3)

        # 充值不能用减法
        rst, msg = MerchantBalanceEvent.update_balance(
            merchant=MerchantEnum.TEST,
            ref_id=ref_id,
            bl_type=BalanceTypeEnum.AVAILABLE,
            source=OrderSourceEnum.TESTING,
            order_type=PayTypeEnum.DEPOSIT,
            ad_type=BalanceAdjustTypeEnum.MINUS,
            value=120.00,
            tx_id=OrderUtils.gen_normal_tx_id(100),
        )
        self.assertEqual(rst, -3)

        # 只有充值才能修改在途余额
        rst, msg = MerchantBalanceEvent.update_balance(
            merchant=MerchantEnum.TEST,
            ref_id=ref_id,
            bl_type=BalanceTypeEnum.INCOME,
            source=OrderSourceEnum.TESTING,
            order_type=PayTypeEnum.WITHDRAW,
            ad_type=BalanceAdjustTypeEnum.MINUS,
            value=120.00,
            tx_id=OrderUtils.gen_normal_tx_id(100),
        )
        self.assertEqual(rst, -4)

        # 在途余额不能从提款减少
        rst, msg = MerchantBalanceEvent.update_balance(
            merchant=MerchantEnum.TEST,
            ref_id=ref_id,
            bl_type=BalanceTypeEnum.INCOME,
            source=OrderSourceEnum.TESTING,
            order_type=PayTypeEnum.WITHDRAW,
            ad_type=BalanceAdjustTypeEnum.MINUS,
            value=120.00,
            tx_id=OrderUtils.gen_normal_tx_id(100),
        )
        self.assertEqual(rst, -4)

        # 人工操作时，必填调整类型
        rst, msg = MerchantBalanceEvent.update_balance(
            merchant=MerchantEnum.TEST,
            ref_id=ref_id,
            source=OrderSourceEnum.MANUALLY,
            bl_type=BalanceTypeEnum.AVAILABLE,
            order_type=PayTypeEnum.MANUALLY,
            value=1.00,
            tx_id=OrderUtils.gen_normal_tx_id(100),
        )
        self.assertEqual(rst, -5)

        # 人工操作时，必填调整备注信息
        rst, msg = MerchantBalanceEvent.update_balance(
            merchant=MerchantEnum.TEST,
            ref_id=ref_id,
            source=OrderSourceEnum.MANUALLY,
            bl_type=BalanceTypeEnum.AVAILABLE,
            ad_type=BalanceAdjustTypeEnum.PLUS,
            order_type=PayTypeEnum.MANUALLY,
            value=1.00,
            tx_id=OrderUtils.gen_normal_tx_id(100),
        )
        self.assertEqual(rst, -5)

        # 在途余额不能人工增加
        rst, msg = MerchantBalanceEvent.update_balance(
            merchant=MerchantEnum.TEST,
            ref_id=ref_id,
            bl_type=BalanceTypeEnum.INCOME,
            source=OrderSourceEnum.MANUALLY,
            order_type=PayTypeEnum.MANUALLY,
            ad_type=BalanceAdjustTypeEnum.PLUS,
            value=120.00,
            tx_id=OrderUtils.gen_normal_tx_id(100),
            comment='xxx',
        )
        self.assertEqual(rst, -6)

        # 冻结余额不能从提款减少
        rst, msg = MerchantBalanceEvent.update_balance(
            merchant=MerchantEnum.TEST,
            ref_id=ref_id,
            bl_type=BalanceTypeEnum.FROZEN,
            source=OrderSourceEnum.TESTING,
            order_type=PayTypeEnum.WITHDRAW,
            ad_type=BalanceAdjustTypeEnum.MINUS,
            value=120.00,
            tx_id=OrderUtils.gen_normal_tx_id(100),
        )
        self.assertEqual(rst, -7)

        # 冻结余额不能从充值增加
        rst, msg = MerchantBalanceEvent.update_balance(
            merchant=MerchantEnum.TEST,
            ref_id=ref_id,
            bl_type=BalanceTypeEnum.FROZEN,
            source=OrderSourceEnum.TESTING,
            order_type=PayTypeEnum.DEPOSIT,
            ad_type=BalanceAdjustTypeEnum.PLUS,
            value=120.00,
            tx_id=OrderUtils.gen_normal_tx_id(100),
        )
        self.assertEqual(rst, -7)

    # def __query_event(self):
    #     # 总共有一个事件
    #     all_events = MerchantBalanceEvent.query_all()
    #     self.assertEqual(len(all_events), 1)
    #
    #     # 查询时不给参数
    #     event = MerchantBalanceEvent.query_event()
    #     self.assertIsNone(event)
    #
    #     # 只给商户名称
    #     events = list(MerchantBalanceEvent.query_event(
    #         merchant=MerchantEnum.TEST,
    #     ))
    #     self.assertEqual(len(events), 1)
    #     event = events[0]
    #     self.assertEqual(event.merchant, MerchantEnum.TEST)
    #     self.assertEqual(event.bl_type, BalanceTypeEnum.AVAILABLE)
    #     self.assertEqual(event.ad_type, BalanceAdjustTypeEnum.PLUS)
    #     self.assertEqual(event.value, 1000)
    #     self.assertEqual(event.order_id, 10)
    #
    #     # 只给source
    #     events = list(MerchantBalanceEvent.query_event(
    #         source=PayTypeEnum.DEPOSIT,
    #     ))
    #     self.assertEqual(len(events), 1)
    #     event = events[0]
    #     self.assertEqual(event.merchant, MerchantEnum.TEST)
    #     self.assertEqual(event.bl_type, BalanceTypeEnum.AVAILABLE)
    #     self.assertEqual(event.ad_type, BalanceAdjustTypeEnum.PLUS)
    #     self.assertEqual(event.value, 1000)
    #     self.assertEqual(event.order_id, 10)
    #
    #     # 只给bl_type
    #     events = list(MerchantBalanceEvent.query_event(
    #         bl_type=BalanceTypeEnum.AVAILABLE,
    #     ))
    #     self.assertEqual(len(events), 1)
    #     event = events[0]
    #     self.assertEqual(event.merchant, MerchantEnum.TEST)
    #     self.assertEqual(event.bl_type, BalanceTypeEnum.AVAILABLE)
    #     self.assertEqual(event.ad_type, BalanceAdjustTypeEnum.PLUS)
    #     self.assertEqual(event.value, 1000)
    #     self.assertEqual(event.order_id, 10)
    #
    #     # 只给ad_type
    #     events = list(MerchantBalanceEvent.query_event(
    #         ad_type=BalanceAdjustTypeEnum.PLUS,
    #     ))
    #     self.assertEqual(len(events), 1)
    #     event = events[0]
    #     self.assertEqual(event.merchant, MerchantEnum.TEST)
    #     self.assertEqual(event.bl_type, BalanceTypeEnum.AVAILABLE)
    #     self.assertEqual(event.ad_type, BalanceAdjustTypeEnum.PLUS)
    #     self.assertEqual(event.value, 1000)
    #     self.assertEqual(event.order_id, 10)
    #
    #     # 只给order_id
    #     events = list(MerchantBalanceEvent.query_event(
    #         order_id=10,
    #     ))
    #     self.assertEqual(len(events), 1)
    #     event = events[0]
    #     self.assertEqual(event.merchant, MerchantEnum.TEST)
    #     self.assertEqual(event.bl_type, BalanceTypeEnum.AVAILABLE)
    #     self.assertEqual(event.ad_type, BalanceAdjustTypeEnum.PLUS)
    #     self.assertEqual(event.value, 1000)
    #     self.assertEqual(event.order_id, 10)
    #
    #     # 参数齐全
    #     events = list(MerchantBalanceEvent.query_event(
    #         merchant=MerchantEnum.TEST,
    #         source=PayTypeEnum.DEPOSIT,
    #         bl_type=BalanceTypeEnum.AVAILABLE,
    #         ad_type=BalanceAdjustTypeEnum.PLUS,
    #         order_id=10,
    #     ))
    #     self.assertEqual(len(events), 1)
    #     event = events[0]
    #     self.assertEqual(event.merchant, MerchantEnum.TEST)
    #     self.assertEqual(event.bl_type, BalanceTypeEnum.AVAILABLE)
    #     self.assertEqual(event.ad_type, BalanceAdjustTypeEnum.PLUS)
    #     self.assertEqual(event.value, 1000)
    #     self.assertEqual(event.order_id, 10)
    #
    #     # 参数多个
    #     events = list(MerchantBalanceEvent.query_event(
    #         merchant=MerchantEnum.TEST,
    #         source=PayTypeEnum.DEPOSIT,
    #         ad_type=BalanceAdjustTypeEnum.PLUS,
    #     ))
    #     self.assertEqual(len(events), 1)
    #     event = events[0]
    #     self.assertEqual(event.merchant, MerchantEnum.TEST)
    #     self.assertEqual(event.bl_type, BalanceTypeEnum.AVAILABLE)
    #     self.assertEqual(event.ad_type, BalanceAdjustTypeEnum.PLUS)
    #     self.assertEqual(event.value, 1000)
    #     self.assertEqual(event.order_id, 10)

    def __create_merchant_info(self):
        # 创建商户TEST
        merchant = MerchantInfo.create_merchant(MerchantEnum.TEST, MerchantTypeEnum.TEST)
        self.assertEqual(merchant.id, 1)
        self.assertEqual(merchant.merchant, MerchantEnum.TEST)
        self.assertEqual(merchant.m_type, MerchantTypeEnum.TEST)
        self.assertEqual(merchant.state, AccountStateEnum.ACTIVE)

        # 创建商户QF2
        merchant = MerchantInfo.create_merchant(MerchantEnum.QF2, MerchantTypeEnum.NORMAL)
        self.assertEqual(merchant.id, 2)
        self.assertEqual(merchant.merchant, MerchantEnum.QF2)
        self.assertEqual(merchant.m_type, MerchantTypeEnum.NORMAL)
        self.assertEqual(merchant.state, AccountStateEnum.ACTIVE)

        # 创建商户QF3
        merchant = MerchantInfo.create_merchant(MerchantEnum.QF3, MerchantTypeEnum.NORMAL)
        self.assertEqual(merchant.id, 3)
        self.assertEqual(merchant.merchant, MerchantEnum.QF3)
        self.assertEqual(merchant.m_type, MerchantTypeEnum.NORMAL)
        self.assertEqual(merchant.state, AccountStateEnum.ACTIVE)

        # 应该有3个商户
        all_merchant = list(MerchantInfo.query_all())
        self.assertEqual(len(all_merchant), 3)

        # 删除TEST商户
        MerchantInfo.delete_merchant(MerchantEnum.TEST)

        # 还有2个商户
        all_merchant = list(MerchantInfo.query_all())
        self.assertEqual(len(all_merchant), 2)

        # 查不到TEST商户
        merchant = MerchantInfo.query_merchant(MerchantEnum.TEST)
        self.assertIsNone(merchant)

        # 再次添加TEST商户
        merchant = MerchantInfo.create_merchant(MerchantEnum.TEST, MerchantTypeEnum.TEST)
        self.assertEqual(merchant.id, 4)
        self.assertEqual(merchant.merchant, MerchantEnum.TEST)
        self.assertEqual(merchant.m_type, MerchantTypeEnum.TEST)
        self.assertEqual(merchant.state, AccountStateEnum.ACTIVE)

        # 又有3个商户
        all_merchant = list(MerchantInfo.query_all())
        self.assertEqual(len(all_merchant), 3)

    def __add_event(self):
        ###############################################################
        # 可用余额加减测试
        ###############################################################
        msg = "事件:1, 可用余额, 存款增加 1000，成功，余额增加"
        data = dict(
            merchant=MerchantEnum.TEST,
            source=OrderSourceEnum.TESTING,
            order_type=PayTypeEnum.DEPOSIT,
            bl_type=BalanceTypeEnum.AVAILABLE,
            ad_type=BalanceAdjustTypeEnum.PLUS,
            value=Decimal("10.00"),
            comment=msg,
        )
        balance_check = dict(
            balance_available=data['value'],
            balance_frozen=0,
            balance_income=0,
        )
        event_check = dict(total=1)
        event_check.update(data)
        self.__change_balance(data=data, result=0, balance_check=balance_check, event_check=event_check)

        # self.__query_event()

        ###############################################################
        msg = "事件:2, 可用余额, 存款增加 80，成功"
        data.update(
            source=OrderSourceEnum.TESTING,
            order_type=PayTypeEnum.DEPOSIT,
            bl_type=BalanceTypeEnum.AVAILABLE,
            ad_type=BalanceAdjustTypeEnum.PLUS,
            value=Decimal("0.80"),
            comment=msg,
        )
        balance_check['balance_available'] = Decimal("10.80")  # 1000 + 80 = 1080
        event_check.update(total=2)
        event_check.update(data)
        self.__change_balance(data=data, result=0, balance_check=balance_check, event_check=event_check)

        ###############################################################
        msg = "事件:3, 可用余额, 提款300，成功，余额减少，事件增加"
        data.update(
            source=OrderSourceEnum.TESTING,
            order_type=PayTypeEnum.WITHDRAW,
            bl_type=BalanceTypeEnum.AVAILABLE,
            ad_type=BalanceAdjustTypeEnum.MINUS,
            value=Decimal("3.00"),
            comment=msg,
        )
        balance_check['balance_available'] = Decimal("7.80")  # 1080 - 300 = 780
        event_check.update(total=3)
        event_check.update(data)
        self.__change_balance(data=data, result=0, balance_check=balance_check, event_check=event_check)

        ###############################################################
        msg = "事件:4, 可用余额, 提款300，成功，余额减少，事件增加"
        data.update(
            source=OrderSourceEnum.TESTING,
            order_type=PayTypeEnum.WITHDRAW,
            bl_type=BalanceTypeEnum.AVAILABLE,
            ad_type=BalanceAdjustTypeEnum.MINUS,
            value=Decimal("7.80"),
            comment=msg,
        )
        balance_check['balance_available'] = 0  # 780 - 780 = 0
        event_check.update(total=4)
        event_check.update(data)
        self.__change_balance(data=data, result=0, balance_check=balance_check, event_check=event_check)

        ###############################################################
        msg = "余额不足, 可用余额, 提款1000，失败，余额不足，更新事件回滚"
        data.update(
            source=OrderSourceEnum.TESTING,
            order_type=PayTypeEnum.WITHDRAW,
            bl_type=BalanceTypeEnum.AVAILABLE,
            ad_type=BalanceAdjustTypeEnum.MINUS,
            value=Decimal("100.00"),
            comment=msg,
        )
        self.__change_balance(data=data, result=-101, balance_check=balance_check, event_check=event_check)

        ###############################################################
        msg = "余额不足, 可用余额, 手动减 1000，失败，余额不足，更新事件回滚"
        data.update(
            source=OrderSourceEnum.MANUALLY,
            bl_type=BalanceTypeEnum.AVAILABLE,
            ad_type=BalanceAdjustTypeEnum.MINUS,
            value=Decimal("100.00"),
            comment=msg,
        )
        self.__change_balance(data=data, result=-101, balance_check=balance_check, event_check=event_check)

        ###############################################################
        # 在途余额加减测试,只有订单充值能增加在途余额，人工减少在途余额
        ###############################################################
        msg = "事件:5, 在途余额, 存款 800，成功"
        data.update(
            source=OrderSourceEnum.TESTING,
            order_type=PayTypeEnum.DEPOSIT,
            bl_type=BalanceTypeEnum.INCOME,
            ad_type=BalanceAdjustTypeEnum.PLUS,
            value=Decimal("8.00"),
            comment=msg,
        )
        balance_check['balance_income'] = data['value']  # 800
        event_check.update(total=5)
        event_check.update(data)
        self.__change_balance(data=data, result=0, balance_check=balance_check, event_check=event_check)

        ###############################################################
        msg = "事件:6, 在途余额, 人工减去 800，成功，减掉的在途余额变成了可用余额"
        data.update(
            source=OrderSourceEnum.MANUALLY,
            bl_type=BalanceTypeEnum.INCOME,
            ad_type=BalanceAdjustTypeEnum.MINUS,
            value=Decimal("8.00"),
            comment=msg,
        )
        balance_check['balance_income'] = 0  # 800 - 800 = 0
        balance_check['balance_available'] += Decimal("8.00")
        event_check.update(total=6)
        event_check.update(data)
        self.__change_balance(data=data, result=0, balance_check=balance_check, event_check=event_check)

        ###############################################################
        msg = "余额不足, 在途余额, 手动减少 12000，失败，在途余额不足"
        data.update(
            source=OrderSourceEnum.MANUALLY,
            bl_type=BalanceTypeEnum.INCOME,
            ad_type=BalanceAdjustTypeEnum.MINUS,
            value=Decimal("120.00"),
            comment=msg,
        )
        self.__change_balance(data=data, result=-101, balance_check=balance_check, event_check=event_check)

        ###############################################################
        # 冻结余额加减测试，冻结余额和可用余额互相抵消
        ###############################################################
        msg = "事件:7, 冻结余额, 人工增加300，成功，余额增加，事件+1"
        data.update(
            source=OrderSourceEnum.MANUALLY,
            bl_type=BalanceTypeEnum.FROZEN,
            ad_type=BalanceAdjustTypeEnum.PLUS,
            value=Decimal("3.00"),
            comment=msg,
        )
        balance_check['balance_frozen'] = data['value']  # 300
        balance_check['balance_available'] -= data['value']  # 800 - 300 = 500
        event_check.update(total=7)
        event_check.update(data)
        self.__change_balance(data=data, result=0, balance_check=balance_check, event_check=event_check)

        ###############################################################
        msg = "事件:8, 冻结余额, 人工增加300，成功，余额增加，事件+1"
        data.update(
            source=OrderSourceEnum.MANUALLY,
            bl_type=BalanceTypeEnum.FROZEN,
            ad_type=BalanceAdjustTypeEnum.MINUS,
            value=Decimal("2.00"),
            comment=msg,
        )
        balance_check['balance_frozen'] -= data['value']  # 300 - 200 = 100
        balance_check['balance_available'] += data['value']  # 500 + 200 = 700
        event_check.update(total=8)
        event_check.update(data)
        self.__change_balance(data=data, result=0, balance_check=balance_check, event_check=event_check)

        ###############################################################
        msg = "余额不足, 冻结余额，人工减去 10000，失败，在途余额不足"
        data.update(
            source=OrderSourceEnum.MANUALLY,
            bl_type=BalanceTypeEnum.INCOME,
            ad_type=BalanceAdjustTypeEnum.MINUS,
            value=Decimal("100.00"),
            comment=msg,
        )
        self.__change_balance(data=data, result=-101, balance_check=balance_check, event_check=event_check)

        ###############################################################
        # 商户切换测试
        ###############################################################
        msg = "QF2事件:1, 人工对qf2的可用余额减少 1000，成功"
        data.update(
            merchant=MerchantEnum.QF2,
            source=OrderSourceEnum.MANUALLY,
            bl_type=BalanceTypeEnum.AVAILABLE,
            ad_type=BalanceAdjustTypeEnum.PLUS,
            value=Decimal("10.00"),
            comment=msg,
        )
        balance_check = dict(
            balance_available=data['value'],
            balance_frozen=0,
            balance_income=0,
        )
        event_check.update(total=1)
        event_check.update(data)
        self.__change_balance(data=data, result=0, balance_check=balance_check, event_check=event_check)

        ###############################################################
        msg = "QF2事件:2, 人工对qf2的可用余额减少 1000，成功"
        data.update(
            merchant=MerchantEnum.QF2,
            source=OrderSourceEnum.MANUALLY,
            bl_type=BalanceTypeEnum.AVAILABLE,
            ad_type=BalanceAdjustTypeEnum.MINUS,
            value=Decimal("10.00"),
            comment=msg,
        )
        balance_check['balance_available'] -= data['value']  # 0
        event_check.update(total=2)
        event_check.update(data)
        self.__change_balance(data=data, result=0, balance_check=balance_check, event_check=event_check)

        ###############################################################
        # 余额不足
        self.__change_balance(data=data, result=-101, balance_check=balance_check, event_check=event_check)
