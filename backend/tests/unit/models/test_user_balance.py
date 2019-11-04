import copy
import hashlib
from decimal import Decimal

from app.enums.trade import PayTypeEnum, BalanceTypeEnum, BalanceAdjustTypeEnum, OrderSourceEnum
from app.libs.datetime_kit import DateTimeKit
from app.libs.order_kit import OrderUtils
from app.libs.string_kit import RandomString
from app.models.balance import UserBalance, UserBalanceEvent
from config import MerchantEnum
from tests import TestCashierUnitBase


class TestMerchantBalanceModel(TestCashierUnitBase):
    ENABLE_PRINT = False
    ENABLE_SQL_LOG = False

    def test_merchant_model(self):

        for uid in range(1000, 1020):
            for merchant in MerchantEnum:
                uid += merchant.value
                UserBalance.create_user_balance(uid, merchant)
                self.__check_event_params_error(uid, merchant)
                self.__add_event(uid, merchant)

        x = 1

    def __change_balance(self, data: dict, result: int, balance_check: dict):
        """
        修改
        :param data:
        :param result:
        :param balance_check:
        :return:
        """
        # 修改余额
        data = copy.deepcopy(data)
        ref_id = OrderUtils.gen_unique_ref_id()
        data['ref_id'] = ref_id
        data['tx_id'] = OrderUtils.gen_normal_tx_id(data['uid'])

        rst, msg = UserBalanceEvent.update_user_balance(**data)
        self.assertEqual(result, rst)

        # 验证余额
        balance = UserBalance.query_balance(data['uid'], data['merchant']).first()
        self.assertIsNotNone(balance)
        self.assertEqual(balance_check['balance_available'], balance.real_balance)

        if rst != 0:
            # 更新失败，就不用验证结果事件了
            return rst

        event = UserBalanceEvent.query_event(uid=data['uid'], merchant=balance.merchant,
                                             date=DateTimeKit.get_cur_datetime(),
                                             ref_id=ref_id).first()
        value = data['value']
        if data['ad_type'] == BalanceAdjustTypeEnum.MINUS:
            # 做减法
            value = -data['value']

        self.assertEqual(data['uid'], event.uid)
        self.assertEqual(data['merchant'], event.merchant)
        self.assertEqual(data['source'], event.source)
        self.assertEqual(data['bl_type'], event.bl_type)
        self.assertEqual(data['ad_type'], event.ad_type)
        self.assertEqual(value, event.value_real)
        self.assertEqual(ref_id, event.ref_id)

        if data['source'] == OrderSourceEnum.MANUALLY:
            self.assertEqual(data['comment'], event.comment)

        return rst

    def __check_event_params_error(self, uid, merchant):
        ###########################################################
        # 余额修改,参数错误
        ###########################################################

        ref_id = hashlib.md5('lakjdflasjfadl;kfja'.encode('utf8')).hexdigest()

        data = dict(
            uid=uid,
            merchant=merchant,
            ref_id=ref_id,
            source=OrderSourceEnum.TESTING,
            order_type=PayTypeEnum.DEPOSIT,
            bl_type=BalanceTypeEnum.AVAILABLE,
            ad_type=BalanceAdjustTypeEnum.PLUS,
            tx_id=OrderUtils.gen_normal_tx_id(uid),
            value=Decimal("0"),
            comment="xxx",
        )

        # value是0
        rst, msg = UserBalanceEvent.update_user_balance(**data)
        self.assertEqual(rst, -1)

        # value是负数
        data['value'] = Decimal("-100")
        rst, msg = UserBalanceEvent.update_user_balance(**data)
        self.assertEqual(rst, -1)

        # 提款不能用加法
        data['value'] = Decimal("100")
        data['source'] = OrderSourceEnum.TESTING
        data['order_type'] = PayTypeEnum.WITHDRAW
        data['ad_type'] = BalanceAdjustTypeEnum.PLUS
        rst, msg = UserBalanceEvent.update_user_balance(**data)
        self.assertEqual(rst, -3)

        # 充值不能用减法
        data['source'] = OrderSourceEnum.TESTING
        data['order_type'] = PayTypeEnum.DEPOSIT
        data['ad_type'] = BalanceAdjustTypeEnum.MINUS
        rst, msg = UserBalanceEvent.update_user_balance(**data)
        self.assertEqual(rst, -3)

        # 人工操作时，必填调整类型
        data['source'] = OrderSourceEnum.MANUALLY
        data.pop('ad_type')
        rst, msg = UserBalanceEvent.update_user_balance(**data)
        self.assertEqual(rst, -4)

        # 人工操作时，必填调整备注信息
        data['ad_type'] = BalanceAdjustTypeEnum.MINUS
        data.pop('comment')
        rst, msg = UserBalanceEvent.update_user_balance(**data)
        self.assertEqual(rst, -4)

    # def __query_event(self):
    #     # 总共有一个事件
    #     all_events = UserBalanceEvent.query_all()
    #     self.assertEqual(len(all_events), 1)
    #
    #     # 查询时不给参数
    #     event = UserBalanceEvent.query_event()
    #     self.assertIsNone(event)
    #
    #     # 只给商户名称
    #     events = list(UserBalanceEvent.query_event(
    #         merchant=merchant,
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
    #     events = list(UserBalanceEvent.query_event(
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
    #     events = list(UserBalanceEvent.query_event(
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
    #     events = list(UserBalanceEvent.query_event(
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
    #     events = list(UserBalanceEvent.query_event(
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
    #     events = list(UserBalanceEvent.query_event(
    #         merchant=merchant,
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
    #     events = list(UserBalanceEvent.query_event(
    #         merchant=merchant,
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

    def __add_event(self, uid, merchant):
        ###############################################################
        # 可用余额加减测试
        ###############################################################
        msg = "事件:1, 可用余额, 存款增加 1000，成功，余额增加"
        data = dict(
            uid=uid,
            merchant=merchant,
            source=OrderSourceEnum.TESTING,
            order_type=PayTypeEnum.DEPOSIT,
            bl_type=BalanceTypeEnum.AVAILABLE,
            ad_type=BalanceAdjustTypeEnum.PLUS,
            value=Decimal("10.00"),
            comment=msg,
        )
        balance_check = dict(
            balance_available=data['value'],
        )
        self.__change_balance(data=data, result=0, balance_check=balance_check)

        # self.__query_event()

        ###############################################################
        msg = "事件:2, 可用余额, 存款增加 80，成功"
        data.update(
            order_type=PayTypeEnum.DEPOSIT,
            bl_type=BalanceTypeEnum.AVAILABLE,
            ad_type=BalanceAdjustTypeEnum.PLUS,
            value=Decimal("0.80"),
            comment=msg,
        )
        balance_check['balance_available'] = Decimal("10.80")  # 1000 + 80 = 1080
        self.__change_balance(data=data, result=0, balance_check=balance_check)

        ###############################################################
        msg = "事件:3, 可用余额, 提款300，成功，余额减少，事件增加"
        data.update(
            order_type=PayTypeEnum.WITHDRAW,
            bl_type=BalanceTypeEnum.AVAILABLE,
            ad_type=BalanceAdjustTypeEnum.MINUS,
            value=Decimal("3.00"),
            comment=msg,
        )
        balance_check['balance_available'] = Decimal("7.80")  # 1080 - 300 = 780
        self.__change_balance(data=data, result=0, balance_check=balance_check)

        ###############################################################
        msg = "事件:4, 可用余额, 提款300，成功，余额减少，事件增加"
        data.update(
            order_type=PayTypeEnum.WITHDRAW,
            bl_type=BalanceTypeEnum.AVAILABLE,
            ad_type=BalanceAdjustTypeEnum.MINUS,
            value=Decimal("7.80"),
            comment=msg,
        )
        balance_check['balance_available'] = 0  # 780 - 780 = 0
        self.__change_balance(data=data, result=0, balance_check=balance_check)

        ###############################################################
        msg = "余额不足, 可用余额, 提款1000，失败，余额不足，更新事件回滚"
        data.update(
            order_type=PayTypeEnum.WITHDRAW,
            bl_type=BalanceTypeEnum.AVAILABLE,
            ad_type=BalanceAdjustTypeEnum.MINUS,
            value=Decimal("100.00"),
            comment=msg,
        )
        self.__change_balance(data=data, result=-101, balance_check=balance_check)

        ###############################################################
        msg = "余额不足, 可用余额, 手动减 1000，失败，余额不足，更新事件回滚"
        data.update(
            source=OrderSourceEnum.MANUALLY,
            bl_type=BalanceTypeEnum.AVAILABLE,
            ad_type=BalanceAdjustTypeEnum.MINUS,
            value=Decimal("100.00"),
            comment=msg,
        )
        self.__change_balance(data=data, result=-101, balance_check=balance_check)

        ###############################################################
        msg = "手动添加增加用户余额，成功"
        data.update(
            source=OrderSourceEnum.MANUALLY,
            bl_type=BalanceTypeEnum.AVAILABLE,
            ad_type=BalanceAdjustTypeEnum.PLUS,
            value=Decimal("100.00"),
            comment=msg,
        )
        balance_check['balance_available'] = data['value']
        self.__change_balance(data=data, result=0, balance_check=balance_check)

        ###############################################################
        msg = "手动添加增加用户余额，成功"
        data.update(
            source=OrderSourceEnum.MANUALLY,
            bl_type=BalanceTypeEnum.AVAILABLE,
            ad_type=BalanceAdjustTypeEnum.MINUS,
            value=Decimal("100.00"),
            comment=msg,
        )
        balance_check['balance_available'] = 0
        self.__change_balance(data=data, result=0, balance_check=balance_check)
