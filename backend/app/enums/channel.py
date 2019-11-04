import importlib
from enum import unique

from app.enums.base_enum import BaseEnum
from app.enums.third_config import ThirdPayConfig
from app.enums.third_enum import SdkRenderType
from app.enums.trade import PaymentTypeEnum, PayMethodEnum, PayTypeEnum
from app.libs.dict_object import DictObject


class DictObjectConfig(DictObject):
    """
    找不到的属性，从 _config 里面找
    """

    def __getattr__(self, item):
        if item in self:
            return self.get(item)

        _config = self.get('_config')
        if isinstance(_config, (dict,)):
            return _config.get(item)

        return None

    __getitem__ = __getattr__


@unique
class ChannelConfigEnum(BaseEnum):
    """
    通道配置，一个通道会有多个商户，一个商户会不同支付类型（充值/提现），充值里面区分支付方式
    习惯性约束，非强制约束：
    个位区分支付方式，十位区分支付类型，千位区分商户号，万位或以上区分提供商
    """
    # 立马付充值
    CHANNEL_1001 = 1001
    CHANNEL_1002 = 1002
    CHANNEL_1003 = 1003
    # 立马付代付
    CHANNEL_1010 = 1010

    # 专一付代付
    CHANNEL_2010 = 2010
    # 专一付 代收
    CHANNEL_2003 = 2003

    # 快汇支付
    CHANNEL_3001 = 3001
    CHANNEL_3002 = 3002

    # 极付充值
    # 1:支付宝
    CHANNEL_7001 = 7001

    # 银扫支付
    CHANNEL_4003 = 4003
    CHANNEL_4010 = 4010

    # One pay
    CHANNEL_5003 = 5003

    # One pay QR ZHIFUBAO
    CHANNEL_5010 = 5010
    CHANNEL_5011 = 5011
    # One pay QR 云闪付
    CHANNEL_5013 = 5013
    # One pay 代付
    CHANNEL_5020 = 5020

    # Xft 支付宝扫码

    CHANNEL_6001 = 6001

    # Xft 支付宝H5

    CHANNEL_6002 = 6002

    # # Xft 微信 扫码 todo: 有问题
    #
    # CHANNEL_6004 = 6004
    # 信付通 云闪付
    CHANNEL_6005 = 6005
    # # # todo: 删除
    # CHANNEL_6006 = 6006

    # 信付通 小额代付
    CHANNEL_6013 = 6013
    # 信付通 大额代付
    CHANNEL_6014 = 6014

    # vpay 支付宝充值
    CHANNEL_8001 = 8001
    # vpay 银行卡充值
    CHANNEL_8002 = 8002
    # vpay 云闪付
    CHANNEL_8003 = 8003

    # rukoumy 支付宝扫码
    CHANNEL_9001 = 9001
    # rukoumy 微信扫码
    CHANNEL_9002 = 9002

    CHANNEL_10001 = 10001

    # 统一付 云闪付
    CHANNEL_11001 = 11001

    # Gpay 支付宝扫码
    CHANNEL_12001 = 12001

    @property
    def desc(self):
        """
        中文描述
        :return:
        """
        return '|'.join(map(str, [self.value, self.conf.provider,
                                  self.conf.payment_method.desc if self.conf.payment_method else '代付']))

    @property
    def is_deposit(self):
        return bool(self.conf.payment_method)

    @classmethod
    def get_deposit_desc_name_pairs(cls):
        return [dict(desc=x.desc, name=x.name) for x in cls if x.is_deposit]

    @classmethod
    def get_withdraw_desc_name_pairs(cls):
        return [dict(desc=x.desc, name=x.name) for x in cls if not x.is_deposit]

    def get_launch_pay_func(self, pay_type: PayTypeEnum):
        """
        获取发起第三方支付请求的函数
        :param pay_type:
        :return:
        """
        cls_name = 'request_cls' if pay_type == PayTypeEnum.DEPOSIT else 'withdraw_cls'
        paths = self.conf[cls_name].split('.')
        module_path = '.'.join(paths[:-1])
        module = importlib.import_module(module_path)
        request_cls = getattr(module, paths[-1])
        request_obj = request_cls(self)
        return getattr(request_obj, 'launch_pay')

    def plus_fee_for_withdraw(self):
        """
        需要把手续费加到发起金额的代付通道
        :return:
        """
        return self in [
            self.CHANNEL_2010,
        ]

    def get_prompt_info(self):
        """
        特殊通道的备注信息
        不要超过15个汉字
        :return:
        """
        return {
                   self.CHANNEL_8003: "请在跳转后务必填写备注信息",
                   self.CHANNEL_5003: "暂不支持农业银行与工商银行",
                   self.CHANNEL_9001: "只支持10,20,30,50,100面额",
                   self.CHANNEL_9002: "只支持10,20,30,50,100面额",
               }.get(self) or ''

    def get_prompt_info_detail(self):
        return {
                   self.CHANNEL_9001: ["请务必在5分钟内完成付款，逾期支付金额无法退还", ],
                   self.CHANNEL_9002: [
                       "1. 请务必在5分钟内完成付款，逾期支付金额无法退还",
                       "2. 请使用手机浏览器扫码，不可使用微信扫码"
                   ],
               }.get(self) or ''

    def is_fixed_amount_channel(self):
        """
        判断是否是固定额度的通道
        :return:
        """
        payment_type = self.conf.get('payment_type')
        return payment_type and payment_type.is_fixed_amount

    def get_fixed_amounts(self):
        """
        获取固额金额列表
        :return:
        """
        if not self.is_fixed_amount_channel():
            return []

        return {
                   self.CHANNEL_9001: [10, 20, 30, 50, 100],
                   self.CHANNEL_9002: [10, 20, 30, 50, 100],
               }.get(self) or []

    def is_amount_in_fixed_list(self, amount):
        """
        判断金额是否在固定额度列表中
        :param amount:
        :return:
        """
        for fix_amount in self.get_fixed_amounts():
            if fix_amount == amount:
                # 额度匹配
                return True
        return False

    def is_china_ip_required(self):
        """
        只支持境内IP的通道
        :return:
        """
        return self in [
            self.CHANNEL_9001,
            self.CHANNEL_9002,
            self.CHANNEL_5003,
            self.CHANNEL_5010,
            self.CHANNEL_5011,
            self.CHANNEL_5013,
            self.CHANNEL_12001,
        ]

    @property
    def conf(self):
        return {
            # 立马付
            self.CHANNEL_1001:
                DictObjectConfig(
                    _config=ThirdPayConfig.LIMAFU_95632.value,
                    payment_type=PaymentTypeEnum.ZHIFUBAO,
                    payment_method=PayMethodEnum.ZHIFUBAO_SAOMA,
                    third_paytype='ZFB',
                ),
            self.CHANNEL_1002:
                DictObjectConfig(
                    _config=ThirdPayConfig.LIMAFU_95632.value,
                    payment_type=PaymentTypeEnum.ZHIFUBAO,
                    payment_method=PayMethodEnum.ZHIFUBAO_H5,
                    third_paytype='ZFBH5',
                ),
            self.CHANNEL_1003:
                DictObjectConfig(
                    _config=ThirdPayConfig.LIMAFU_95632.value,
                    payment_type=PaymentTypeEnum.YUNSHANFU,
                    payment_method=PayMethodEnum.YUNSHANFU,
                    third_paytype='YSF',
                ),
            self.CHANNEL_1010:
                DictObjectConfig(
                    _config=ThirdPayConfig.LIMAFU_95632.value
                ),

            # 专一付 代付
            self.CHANNEL_2010:
                DictObjectConfig(
                    _config=ThirdPayConfig.ZHUANYIFU_11159.value
                ),
            # 专一付 代收云闪付
            self.CHANNEL_2003:
                DictObjectConfig(
                    _config=ThirdPayConfig.ZHUANYIFU_DEPOSIT_11159.value,
                    payment_type=PaymentTypeEnum.YUNSHANFU,
                    payment_method=PayMethodEnum.YUNSHANFU,
                    third_paytype='YSF',
                ),
            self.CHANNEL_3001:
                DictObjectConfig(
                    _config=ThirdPayConfig.KUAIHUI.value,
                    payment_type=PaymentTypeEnum.BANKCARD,
                    payment_method=PayMethodEnum.BANK_TO_BANK
                ),

            self.CHANNEL_3002:
                DictObjectConfig(
                    _config=ThirdPayConfig.KUAIHUI_0bd0d8.value,
                    payment_type=PaymentTypeEnum.BANKCARD,
                    payment_method=PayMethodEnum.BANK_TO_BANK
                ),

            # 极付充值
            self.CHANNEL_7001:
                DictObjectConfig(
                    _config=ThirdPayConfig.JIFU.value,
                    payment_type=PaymentTypeEnum.ZHIFUBAO,
                    payment_method=PayMethodEnum.ZHIFUBAO_SAOMA,
                    third_paytype='1',  # 第三方的支付类型（pay_type）, 1:支付宝 2:微信 3:银行卡
                ),

            self.CHANNEL_4010:
                DictObjectConfig(
                    _config=ThirdPayConfig.YINSAO_WITHDRAW.value,
                ),
            self.CHANNEL_4003:
                DictObjectConfig(
                    _config=ThirdPayConfig.YINSAO_DEPOSIT.value,
                    payment_type=PaymentTypeEnum.YUNSHANFU,
                    payment_method=PayMethodEnum.YUNSHANFU,
                    third_paytype='YSF',
                ),

            # 易付银联 deposit
            self.CHANNEL_5003:
                DictObjectConfig(
                    _config=ThirdPayConfig.ONE_PAY_DEPOSIT.value,
                    payment_type=PaymentTypeEnum.YINLIAN,
                    payment_method=PayMethodEnum.YINLIAN_KUAIJIE,
                    third_paytype='YSF',
                ),
            # 易付银联 alipay扫码
            self.CHANNEL_5010:
                DictObjectConfig(
                    _config=ThirdPayConfig.ONE_PAY_QR_DEPOSIT.value,
                    payment_type=PaymentTypeEnum.ZHIFUBAO,
                    payment_method=PayMethodEnum.ZHIFUBAO_SAOMA,
                    third_paytype='ZFB',
                ),
            # 易付银联 WEIXIN二维码
            self.CHANNEL_5011:
                DictObjectConfig(
                    _config=ThirdPayConfig.ONE_PAY_QR_DEPOSIT.value,
                    payment_type=PaymentTypeEnum.WEIXIN,
                    payment_method=PayMethodEnum.WEIXIN_SAOMA,
                    third_paytype='WX',
                ),
            # 易付银联 银联云闪付
            self.CHANNEL_5013:
                DictObjectConfig(
                    _config=ThirdPayConfig.ONE_PAY_QR_DEPOSIT.value,
                    payment_type=PaymentTypeEnum.YUNSHANFU,
                    payment_method=PayMethodEnum.YUNSHANFU,
                    third_paytype='YSF',
                ),

            self.CHANNEL_5020:
                DictObjectConfig(
                    _config=ThirdPayConfig.ONE_PAY_WITHDRAW.value,
                ),

            self.CHANNEL_6001:
                DictObjectConfig(
                    _config=ThirdPayConfig.EpayTong_PAY_DEPOSIT.value,
                    payment_type=PaymentTypeEnum.ZHIFUBAO,
                    payment_method=PayMethodEnum.ZHIFUBAO_SAOMA,
                    third_paytype="ZFB"
                ),

            self.CHANNEL_6002:
                DictObjectConfig(
                    _config=ThirdPayConfig.EpayTong_PAY_DEPOSIT.value,
                    payment_type=PaymentTypeEnum.ZHIFUBAO,
                    payment_method=PayMethodEnum.ZHIFUBAO_H5,
                    third_paytype="ZFB"
                ),

            # self.CHANNEL_6004:
            #     DictObjectConfig(
            #         _config=ThirdPayConfig.EpayTong_PAY_DEPOSIT.value,
            #         payment_type=PaymentTypeEnum.WEIXIN,
            #         payment_method=PayMethodEnum.WEIXIN_SAOMA,
            #         third_paytype="WX"
            #     ),
            self.CHANNEL_6005:
                DictObjectConfig(
                    _config=ThirdPayConfig.EpayTong_PAY_DEPOSIT.value,
                    payment_type=PaymentTypeEnum.YUNSHANFU,
                    payment_method=PayMethodEnum.YUNSHANFU,
                    third_paytype="YL"
                ),

            # self.CHANNEL_6006:
            #     DictObjectConfig(
            #         _config=ThirdPayConfig.EpayTong_PAY_DEPOSIT.value,
            #         payment_type=PaymentTypeEnum.YINLIAN,
            #         payment_method=PayMethodEnum.YINLIAN_KUAIJIE,
            #         third_paytype="YL"
            #     ),

            self.CHANNEL_6013:
                DictObjectConfig(
                    _config=ThirdPayConfig.EPAYTONG_PAY_WITHDRAW.value
                ),

            self.CHANNEL_6014:
                DictObjectConfig(
                    _config=ThirdPayConfig.EPAYTONG_LARGE_WITHDRAW.value
                ),

            self.CHANNEL_8001:
                DictObjectConfig(
                    _config=ThirdPayConfig.Vpay_DEPOSIT.value,
                    payment_type=PaymentTypeEnum.ZHIFUBAO,
                    payment_method=PayMethodEnum.ZHIFUBAO_SAOMA,
                    render_type=SdkRenderType.URL,
                    request_config=dict(channel=1),
                ),

            self.CHANNEL_8002:
                DictObjectConfig(
                    _config=ThirdPayConfig.Vpay_DEPOSIT.value,
                    payment_type=PaymentTypeEnum.BANKCARD,
                    payment_method=PayMethodEnum.BANK_TO_BANK,
                    render_type=SdkRenderType.URL,
                    request_config=dict(channel=3),
                ),

            self.CHANNEL_8003:
                DictObjectConfig(
                    _config=ThirdPayConfig.Vpay_DEPOSIT.value,
                    payment_type=PaymentTypeEnum.YUNSHANFU,
                    payment_method=PayMethodEnum.YUNSHANFU,
                    render_type=SdkRenderType.URL,
                    request_config=dict(channel=4),
                ),

            self.CHANNEL_9001:
                DictObjectConfig(
                    _config=ThirdPayConfig.RUKOUMY_DEPOSIT.value,
                    payment_type=PaymentTypeEnum.ZHIFUBAO_FIXED,
                    payment_method=PayMethodEnum.ZHIFUBAO_H5,
                    third_paytype="ZFB"
                ),

            self.CHANNEL_9002:
                DictObjectConfig(
                    _config=ThirdPayConfig.RUKOUMY_DEPOSIT.value,
                    payment_type=PaymentTypeEnum.WEIXIN_FIXED,
                    payment_method=PayMethodEnum.WEIXIN_H5,
                    third_paytype="WX"
                ),
            self.CHANNEL_10001:
                DictObjectConfig(
                    _config=ThirdPayConfig.BESTPAY_DEPOSIT.value,
                    payment_type=PaymentTypeEnum.BANKCARD,
                    payment_method=PayMethodEnum.BANK_TO_BANK,
                    third_paytype="BTB"
                ),
            self.CHANNEL_11001:
                DictObjectConfig(
                    _config=ThirdPayConfig.TONGYI_PAY_DEPOSIT.value,
                    payment_type=PaymentTypeEnum.YUNSHANFU,
                    payment_method=PayMethodEnum.YUNSHANFU,
                    third_paytype="YSF"
                ),
            self.CHANNEL_12001:
                DictObjectConfig(
                    _config=ThirdPayConfig.GPAY_DEPOSIT.value,
                    payment_type=PaymentTypeEnum.ZHIFUBAO,
                    payment_method=PayMethodEnum.ZHIFUBAO_SAOMA,
                    third_paytype="ZFB"
                ),

        }.get(self)


@unique
class ChannelStateEnum(BaseEnum):
    """通道状态"""

    TESTING = 10
    ONLINE = 20
    MAINTAIN = 25
    DISABLE = 40

    @property
    def desc(self):
        return {
            self.TESTING: "测试中",
            self.ONLINE: "已上架",
            self.MAINTAIN: "维护中",
            self.DISABLE: "已下架",
        }.get(self)

    def is_available(self, test=False):
        """
        可用状态
        :return:
        """
        if test:
            # 对测试用户可用的状态
            return self in [self.TESTING, self.ONLINE]

        # 正式用户可用的状态
        return self == self.ONLINE


@unique
class ChannelReasonEnum(BaseEnum):
    """通道不可用原因"""

    MAINTAIN = 1
    DAY_LIMIT = 2
    TRADE_TIME_LIMIT = 3

    @property
    def desc(self):
        return {
            self.MAINTAIN: "通道维护中",
            self.DAY_LIMIT: "达到日交易限额",
            self.TRADE_TIME_LIMIT: "交易时间限制",
        }.get(self)

    def is_available(self, test=False):
        """
        可用状态
        :return:
        """
        if test:
            # 对测试用户可用的状态
            return self in [self.TESTING, self.ONLINE]

        # 正式用户可用的状态
        return self == self.ONLINE


if __name__ == '__main__':
    channel = ChannelConfigEnum.CHANNEL_1001
    print(channel.name, channel.value)

    # 基础属性
    conf = channel.conf
    print(conf.payment_type)
    # 用attr获取属性
    mch_id = conf.mch_id
    print(mch_id)
    # []获取属性
    desc = channel.desc
    print(desc)
