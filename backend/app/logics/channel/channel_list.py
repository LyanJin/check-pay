"""
返回给钱包的通道列表
"""
import copy
import random
from collections import defaultdict
from decimal import Decimal
from operator import attrgetter
from typing import Dict

from app.enums.channel import ChannelConfigEnum
from app.enums.trade import PayTypeEnum, PaymentTypeEnum
from app.logics.channel.chanel_cache import ChannelLimitCacheCtl
from app.models.channel import ChannelConfig, ProxyChannelConfig, ChannelRouter, ChannelRouter2
from app.models.merchant import MerchantFeeConfig
from config import MerchantEnum


class ChannelListHelper:

    @classmethod
    def get_config_channels(cls, payment_way: PayTypeEnum, ret_dict=False):
        if payment_way == PayTypeEnum.DEPOSIT:
            return ChannelConfig.get_latest_active_configs(ret_dict)
        else:
            return ProxyChannelConfig.get_latest_active_configs(ret_dict)

    @classmethod
    def get_router2_dict(cls) -> Dict[ChannelConfigEnum, ChannelRouter2]:
        """
        获取通道路由配置
        :return:
        """
        return {c.channel_enum: c for c in ChannelRouter2.query_all()}

    @classmethod
    def get_available_channels(cls, merchant, payment_way: PayTypeEnum, amount=0, client_ip=None, payment_type=None):
        """
        获取可用的通道
        :param merchant: 
        :param payment_way:
        :param amount:
        :param client_ip:
        :param payment_type:
        :return:
        """

        channels = list()

        # 找出最新版本的商户费率配置
        merchant_fees = MerchantFeeConfig.get_latest_active_configs(merchant=merchant, payment_way=payment_way)
        if not merchant_fees:
            return channels

        # 充值需要判断到通道支付方式是否已经在商户配置费率
        # 提现配置没有payment_method，列表置为空，不用判断
        payment_methods = [m.payment_method for m in merchant_fees if m.payment_method]

        routers_dict = cls.get_router2_dict()
        channel_configs = cls.get_config_channels(payment_way)

        for channel in channel_configs:
            channel_enum = channel.channel_enum

            router = routers_dict.get(channel_enum)
            if router and not router.is_router_match(merchant=merchant, amount=amount):
                continue

            if payment_type and channel_enum.conf['payment_type'] != payment_type:
                # 支付类型不匹配
                continue

            if payment_methods and channel_enum.conf['payment_method'] not in payment_methods:
                # 过滤掉未设置费率的支付方式
                continue

            if not channel.is_channel_valid(merchant.is_test, amount=amount, client_ip=client_ip):
                continue

            channels.append(channel)

        return channels

    @classmethod
    def get_channel_payment_type_router(cls, interface=None, amount=None, merchant=None, uid=None):
        """
        根据匹配条件，选择一组最优的支付类型
        :param merchant:
        :param uid:
        :param interface:
        :param amount:
        :return:
        """
        params = copy.deepcopy(locals())
        params.pop('cls')

        routers = ChannelRouter.query_all()
        router = ChannelRouter.get_one_match_router(routers, **params)
        if not router:
            default_routers = ChannelRouter.get_no_condition_routers(routers)
            if default_routers:
                router = default_routers[0]

        if not router:
            return []

        config_list = router.config_list
        # 按优先级排序，优先级值越小，优先级越高
        return sorted(config_list, key=lambda x: x['priority'])

    @classmethod
    def choice_one_channel_for_payment_type(cls, channels, routers, merchant, amount):
        """
        为每个支付方式选择一个支付通道
        :param channels:
        :param routers:
        :param merchant:
        :param amount:
        :return:
        """
        payment_type_list = list()

        payment_type_dict = cls.choice_channel_by_priority(channels, merchant, amount)

        for payment_type, channel in payment_type_dict.items():
            payment_type_list.append(dict(
                desc=payment_type.desc,
                value=payment_type.value,
                channel_id=channel.channel_enum.value,
                channel_prompt=channel.channel_enum.get_prompt_info(),
                limit_min=channel.limit_per_min,
                limit_max=channel.limit_per_max,
            ))

        # 根据路由方案进行排序
        sorted_payment_type_list = list()
        if routers:
            for router in routers:
                for item in payment_type_list:
                    if router['payment_type'].value == item['value']:
                        sorted_payment_type_list.append(item)
                        break
        else:
            sorted_payment_type_list = payment_type_list

        return sorted_payment_type_list

    @classmethod
    def channels_to_payment_type_dict(cls, channels):
        """
        把所有通道按支付类型分类
        :param channels:
        :return:
        """
        payment_type_dict = defaultdict(list)
        for channel in channels:
            payment_type = channel.channel_enum.conf['payment_type']
            payment_type_dict[payment_type].append(channel)
        return payment_type_dict

    @classmethod
    def choice_one_channel_by_priority(cls, channels, merchant, amount=0):
        """
        根据优先级选择通道，当优先级相同时，随机选择一条通道
        :param channels:
        :param merchant:
        :param amount:
        :return:
        """
        p_channels = channels

        _channels = [c for c in channels if not c.is_amount_per_limit(amount)]
        if amount > 0 and _channels:
            # 使用金额优先匹配通道
            p_channels = _channels

        _channels = [c for c in p_channels if c.is_testing]
        if merchant.is_test and _channels:
            # 如果测试商户，并且有测试通道，只选择测试通道，排除非测试通道
            p_channels = _channels

        if len(set([c.priority for c in p_channels])) == 1:
            # 如果优先级相同，随机选择一条通道
            return random.choice(p_channels)
        else:
            # 按优先级值小到大排序，值越小优先级越高
            return sorted(p_channels, key=attrgetter('priority'))[0]

    @classmethod
    def choice_channel_by_priority(cls, channels, merchant: MerchantEnum, amount=0):
        """
        根据优先级选择通道，当优先级相同时，随机选择一条通道
        :param channels:
        :param merchant:
        :param amount:
        :return:
        """
        payment_type_dict = dict()

        for p_type, p_channels in cls.channels_to_payment_type_dict(channels).items():
            payment_type_dict[p_type] = cls.choice_one_channel_by_priority(p_channels, merchant, amount)

        return payment_type_dict

    @classmethod
    def get_one_channel_by_payment_type(cls, merchant: MerchantEnum, payment_type: PaymentTypeEnum, amount, client_ip):
        """
        获取某个支付类型下面的一个可用的通道
        :param merchant:
        :param payment_type:
        :param amount:
        :param client_ip:
        :return:
        """
        channels = cls.get_available_channels(merchant, payment_way=PayTypeEnum.DEPOSIT, payment_type=payment_type,
                                              amount=amount, client_ip=client_ip)
        if not channels:
            return None

        payment_type_dict = cls.choice_channel_by_priority(channels, merchant, amount)
        return payment_type_dict.get(payment_type)

    @classmethod
    def merge_fixed_amount(cls, channels):
        """
        合并多个通道的固定额度列表
        :param channels:
        :return:
        """
        amounts = list()

        for channel in channels:
            amounts.extend(channel.channel_enum.get_fixed_amounts())

        return amounts

    @classmethod
    def get_channel_min_max(cls, channels):
        """
        获取通道列表中最大最小限额
        :param channels:
        :return:
        """
        limit_min_lst = []
        limit_max_lst = []

        if not channels:
            return 0, 0

        for channel in channels:
            limit_min_lst.append(channel.limit_per_min)
            limit_max_lst.append(channel.limit_per_max)

        limit_min_lst.sort()
        limit_max_lst.sort()

        if not limit_min_lst or not limit_max_lst:
            return 0, 0

        return limit_min_lst[0], limit_max_lst[-1]

    @classmethod
    def get_channels_for_gateway(cls, merchant: MerchantEnum, payment_way: PayTypeEnum, client_ip):
        """
        返回支付网关需要的支付类型配置
        :param merchant:
        :param payment_way:
        :param client_ip:
        :return:
        """
        channels = cls.get_available_channels(merchant=merchant, payment_way=payment_way, client_ip=client_ip)

        payment_type_dict = cls.channels_to_payment_type_dict(channels)

        rst = list()

        for payment_type, channels in payment_type_dict.items():
            item = dict(
                name=payment_type.name,
                limit_min=0,  # 最小限额列表的最小值
                limit_max=0,  # 最大限额列表的最大值
                fixed_amounts=list(),  # 固额列表
            )

            if payment_type.is_fixed_amount:
                item['fixed_amounts'] = cls.merge_fixed_amount(channels)
            else:
                # 这种支付类型下面的最小最大限额列表，已排序
                item['limit_min'], item['limit_max'] = cls.get_channel_min_max(channels)

            rst.append(item)

        return rst

    @classmethod
    def get_channel_limit_range(cls, merchant: MerchantEnum, payment_way: PayTypeEnum, client_ip=None):
        """
        返回支付网关需要的支付类型配置
        :param merchant:
        :param payment_way:
        :param client_ip:
        :return:
        """
        channels = cls.get_available_channels(merchant=merchant, payment_way=payment_way, client_ip=client_ip)
        return cls.get_channel_min_max(channels)

    @classmethod
    def is_amount_out_of_range(cls, amount, merchant, payment_way, client_ip=None):
        """
        判断用户输入金额是否超出当前可用通道的最大最小限额
        :param amount:
        :param merchant:
        :param payment_way:
        :param client_ip:
        :return:
        """
        limit_min, limit_max = cls.get_channel_limit_range(merchant, payment_way, client_ip)
        return amount < limit_min or amount > limit_max
