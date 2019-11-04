from enum import unique

from app.constants.bank_config_list import BANK_CONFIG_DICT
from app.enums.base_enum import BaseEnum


@unique
class PayTypeEnum(BaseEnum):
    """订单类型/支付类型/账变类型"""
    DEPOSIT = 1
    WITHDRAW = 2
    REFUND = 3
    FEE = 4
    TRANSFER = 5
    MANUALLY = 6

    @property
    def desc(self):
        return {
            self.DEPOSIT: "余额充值",
            self.WITHDRAW: "余额提现",
            self.REFUND: "提现退回",
            self.FEE: "手续费",
            self.TRANSFER: "转账",
            self.MANUALLY: "系统调整",
        }.get(self)

    @classmethod
    def is_order_pay(cls, pay_type):
        return pay_type in [cls.DEPOSIT, cls.WITHDRAW]


@unique
class BalanceTypeEnum(BaseEnum):
    """
    余额类型
    """
    AVAILABLE = 1
    INCOME = 2
    FROZEN = 3

    @property
    def desc(self):
        return {
            self.AVAILABLE: "可用余额",
            self.INCOME: "在途余额",
            self.FROZEN: "冻结余额",
        }.get(self)


@unique
class BalanceAdjustTypeEnum(BaseEnum):
    """
    余额变更类型
    """
    PLUS = 1
    MINUS = 2

    @property
    def desc(self):
        return {
            self.PLUS: "增加余额",
            self.MINUS: "减少余额",
        }.get(self)


@unique
class PaymentFeeTypeEnum(BaseEnum):
    """费率类型"""
    PERCENT_PER_ORDER = 1
    YUAN_PER_ORDER = 2

    @property
    def desc(self):
        if self == self.PERCENT_PER_ORDER:
            return "%/笔"
        if self == self.YUAN_PER_ORDER:
            return "元/笔"


@unique
class CostTypeEnum(BaseEnum):
    """扣费类型"""
    MERCHANT = 1
    USER = 2

    @property
    def desc(self):
        return {
            self.MERCHANT: "来自商户",
            self.USER: "来自用户",
        }.get(self)


@unique
class PaymentTypeEnum(BaseEnum):
    """
    支付类型
    """
    ZHIFUBAO = 10
    WEIXIN = 20
    YINLIAN = 30
    YUNSHANFU = 40
    BANKCARD = 50
    JDQIANBAO = 60
    WEIXIN_FIXED = 70
    ZHIFUBAO_FIXED = 80

    @property
    def desc(self):
        """
        中文描述
        :return:
        """
        return {
            self.ZHIFUBAO: "支付宝",
            self.WEIXIN: "微信",
            self.YINLIAN: "银联",
            self.YUNSHANFU: "云闪付",
            self.BANKCARD: "银行卡",
            self.WEIXIN_FIXED: "微信固额",
            self.ZHIFUBAO_FIXED: "支付宝固额",
        }.get(self) or self.name

    @property
    def is_fixed_amount(self):
        """
        判断是否是固定额度的支付类型
        :return:
        """
        return self in [
            self.WEIXIN_FIXED,
            self.ZHIFUBAO_FIXED,
        ]


@unique
class PayMethodEnum(BaseEnum):
    """
    支付方法
    """
    ZHIFUBAO_H5 = 10
    ZHIFUBAO_SAOMA = 20
    WEIXIN_H5 = 30
    WEIXIN_SAOMA = 40
    BANK_TO_BANK = 50
    ZHIFUBAO_TO_BANK = 60
    WEIXIN_TO_BANK = 70
    YINLIAN_KUAIJIE = 80
    YINLIAN_SAOMA = 90
    YUNSHANFU = 100

    @property
    def desc(self):
        return {
            # self.WITHDRAW: "提现",
            self.ZHIFUBAO_H5: "支付宝H5",
            self.ZHIFUBAO_SAOMA: "支付宝扫码",
            self.ZHIFUBAO_TO_BANK: "支付宝转银行卡",
            self.WEIXIN_H5: "微信H5",
            self.WEIXIN_SAOMA: "微信扫码",
            self.WEIXIN_TO_BANK: "微信转银行卡",
            self.BANK_TO_BANK: "银行卡转银行卡",
            self.YINLIAN_KUAIJIE: "银联快捷",
            self.YINLIAN_SAOMA: "银联扫码",
            self.YUNSHANFU: "云闪付",
        }.get(self)

    @property
    def is_h5(self):
        """
        判断是否是H5支付
        :return:
        """
        return self in [
            self.ZHIFUBAO_H5,
            self.WEIXIN_H5,
        ]

    @property
    def map_payment_type(self):
        return {
            self.ZHIFUBAO_H5: PaymentTypeEnum.ZHIFUBAO,
            self.ZHIFUBAO_SAOMA: PaymentTypeEnum.ZHIFUBAO,
            self.ZHIFUBAO_TO_BANK: PaymentTypeEnum.ZHIFUBAO,
            self.WEIXIN_H5: PaymentTypeEnum.WEIXIN,
            self.WEIXIN_SAOMA: PaymentTypeEnum.WEIXIN,
            self.WEIXIN_TO_BANK: PaymentTypeEnum.WEIXIN,
            self.BANK_TO_BANK: PaymentTypeEnum.BANKCARD,
            self.YINLIAN_KUAIJIE: PaymentTypeEnum.YINLIAN,
            self.YINLIAN_SAOMA: PaymentTypeEnum.YINLIAN,
            self.YUNSHANFU: PaymentTypeEnum.YUNSHANFU,
        }.get(self)


@unique
class SettleTypeEnum(BaseEnum):
    """
    结算类型
    """
    # 自然日当天到账
    D0 = 1
    # 自然日第二天到账
    D1 = 2
    # 工作日当天到账, T(trade day)
    T0 = 3
    # 工作日第二天到账, T(trade day)
    T1 = 4


@unique
class SettleStateEnum(BaseEnum):
    """
    结算状态
    """
    INIT = 0
    DONE = 1

    @property
    def desc(self):
        return {
            self.INIT: "未结算",
            self.DONE: "已结算",
        }.get(self)


@unique
class DeliverTypeEnum(BaseEnum):
    """
    出款类型
    """
    SYSTEM = 1
    PROXY = 2
    MANUALLY = 3

    @property
    def desc(self):
        return {
            self.SYSTEM: "系统",
            self.PROXY: "代付",
            self.MANUALLY: "人工",
        }.get(self)


@unique
class DeliverStateEnum(BaseEnum):
    """
    发货状态
    """
    INIT = 0
    DONE = 1
    FAIL = 2

    @property
    def desc(self):
        return {
            self.INIT: "未通知",
            self.DONE: "通知成功",
            self.FAIL: "通知失败",
        }.get(self)


@unique
class PaymentBankEnum(BaseEnum):
    """
    银行类型
    """
    ZHONGGUO = 1
    GONGSHANG = 2
    JIANSHE = 4
    NONGYE = 6
    YOUZHENG = 3
    ZHAOSHANG = 5
    PUFA = 7
    MINSHENG = 8
    PINGAN = 9
    HUAXIA = 10
    ZHONGXIN = 11
    GUANGDA = 12
    XINGYE = 13
    GUANGFA = 14
    JIAOTONG = 15

    @property
    def desc(self):
        """
        中文描述
        :return:
        """
        code = self.bank_code
        return BANK_CONFIG_DICT[code]['bankName']
        # return {
        #     self.ZHONGGUO: "中国银行",
        #     self.GONGSHANG: "工商银行",
        #     self.JIANSHE: "建设银行",
        #     self.NONGYE: "农业银行",
        #     self.YOUZHENG: "邮政储蓄银行",
        #     self.ZHAOSHANG: "招商银行",
        #     self.PUFA: "浦发银行",
        #     self.MINSHENG: "民生银行",
        #     self.PINGAN: "平安银行",
        #     self.HUAXIA: "华夏银行",
        #     self.ZHONGXIN: "中信银行",
        #     self.GUANGDA: "光大银行",
        #     self.XINGYE: "兴业银行",
        #     self.GUANGFA: "广发银行",
        #     self.JIAOTONG: "交通银行",
        # }.get(self)

    @property
    def bank_code(self):
        return {
            self.ZHONGGUO: "BOC",
            self.GONGSHANG: "ICBC",
            self.JIANSHE: "CCB",
            self.NONGYE: "ABC",
            self.YOUZHENG: "PSBC",
            self.ZHAOSHANG: "CMB",
            self.PUFA: "SPDB",
            self.MINSHENG: "CMBC",
            self.PINGAN: "SPABANK",
            self.HUAXIA: "HXBANK",
            self.ZHONGXIN: "CITIC",
            self.GUANGDA: "CEB",
            self.XINGYE: "CIB",
            self.GUANGFA: "GDB",
            self.JIAOTONG: "COMM",
        }.get(self)

    @classmethod
    def get_bank_by_code(cls, code):
        code_bank_dict = dict([(x.bank_code, x) for x in cls])
        return code_bank_dict.get(code)


@unique
class InterfaceTypeEnum(BaseEnum):
    """商户接入类型"""
    CASHIER_H5 = 1
    CASHIER_PC = 2
    API = 3

    @property
    def desc(self):
        return {
            self.CASHIER_H5: "移动端钱包",
            self.CASHIER_PC: "PC端钱包",
            self.API: "开放API",
        }.get(self)


@unique
class OrderSourceEnum(BaseEnum):
    """订单来源"""
    ONLINE = 1
    TESTING = 2
    MANUALLY = 3

    @property
    def desc(self):
        return {
            self.ONLINE: "线上用户",
            self.TESTING: "测试用户",
            self.MANUALLY: "后台人工",
        }.get(self)


@unique
class OrderStateEnum(BaseEnum):
    """订单状态"""
    INIT = 10
    ALLOC = 20
    DEALING = 21
    SUCCESS = 30
    FAIL = 40

    @property
    def desc(self):
        return {
            self.INIT: "订单生成",
            self.ALLOC: "已认领",
            self.DEALING: "处理中",
            self.SUCCESS: "成功",
            self.FAIL: "失败",
        }.get(self)

    @classmethod
    def get_final_states(cls):
        return [cls.SUCCESS, cls.FAIL]

    @property
    def is_final_state(self):
        return self in self.get_final_states()

    @classmethod
    def final_state_desc(cls):
        kv_pairs = ', '.join([': '.join([x.desc, x.name]) for x in cls if x in cls.get_final_states()])
        return "<" + cls.__doc__.strip() + "> {" + kv_pairs + "}"

    def get_back_desc(self, order_type: PayTypeEnum):
        """
        不同类型的订单在不同的状态下有不同的描述
        根据订单来源返回不同的订单描述
        :param order_type:
        :return:
        """
        if self == self.INIT:
            if order_type == PayTypeEnum.WITHDRAW:
                return '待认领'
            else:
                return '未支付'

        elif self == self.SUCCESS:
            if order_type == PayTypeEnum.WITHDRAW:
                return '提现成功'
            else:
                return '充值成功'

        elif self == self.FAIL:
            if order_type == PayTypeEnum.WITHDRAW:
                return '提现失败'
            else:
                return '充值失败'

        return self.desc

    @classmethod
    def get_back_desc_list(cls, order_type: PayTypeEnum):
        kv_pairs = ', '.join([': '.join([x.get_back_desc(order_type), str(x.value)]) for x in cls])
        return "<" + cls.__doc__.strip() + "> {" + kv_pairs + "}"

    def get_cashier_desc(self, order_type: PayTypeEnum):
        """
        不同类型的订单在不同的状态下有不同的描述
        根据订单来源返回不同的订单描述
        :param order_type:
        :return:
        """
        if self == self.INIT:
            if order_type == PayTypeEnum.WITHDRAW:
                return '申请成功'
            else:
                return '等待支付'

        elif self == self.ALLOC:
            if order_type == PayTypeEnum.WITHDRAW:
                return '处理中'

        elif self == self.SUCCESS:
            if order_type == PayTypeEnum.WITHDRAW:
                return '提现成功'
            else:
                return '充值成功'

        elif self == self.FAIL:
            if order_type == PayTypeEnum.WITHDRAW:
                return '提现失败'
            else:
                return '充值失败'

        return self.desc

    @classmethod
    def get_cashier_desc_list(cls, order_type: PayTypeEnum):
        kv_pairs = ', '.join([': '.join([x.get_cashier_desc(order_type), str(x.value)]) for x in cls])
        return "<" + cls.__doc__.strip() + "> {" + kv_pairs + "}"


ZYFBANKS = {'中国工商银行': '0001',
            '中国农业银行': '0002',
            '中国银行': '0003',
            '中国建设银行': '0004',
            '交通银行': '0005',
            '邮政储蓄银行': '0006',
            '中信银行': '1001',
            '中国光大银行': '1002',
            '华夏银行': '1003',
            '中国民生银行': '1004',
            '招商银行': '1005',
            '兴业银行': '1006',
            '广发银行': '1007',
            '平安银行': '1008',
            '上海浦东发展银行': '1009',
            '恒丰银行': '1010',
            '浙商银行': '1011',
            '渤海银行': '1012',
            '北京银行': '2001',
            '上海银行': '2040',
            '南京银行': '2042',
            '杭州银行': '2045',
            '温州银行': '2046',
            '宁波银行': '2055',
            '北京农村商业银行': '3001',
            '上海农商银行': '3018',
            '河北银行': '2003',
            '宁夏银行': '2120',
            '厦门银行': '2130',
            '青岛银行': '2132',
            '江苏银行': '2041',
            '苏州银行': '2044',
            '徽商银行': '2056',
            '九江银行': '2060',
            '上饶银行': '2062',
            '齐鲁银行': '2064',
            '齐商银行': '2065',
            '日照银行': '2070',
            '汉口银行': '2083',
            '广州银行': '2086',
            '东莞银行': '2089',
            '重庆农村商业银行': '3125',
            '深圳农村商业银行': '3137'
            }
