from decimal import Decimal

from flask import current_app

from app.caches.channel_limit import ChannelLimitCache, ChannelDayLimitCache
from app.enums.channel import ChannelConfigEnum
from app.enums.trade import PayTypeEnum
from app.models.channel import ProxyChannelConfig, ChannelConfig


class ChannelLimitCacheCtl:

    def __init__(self, order_type: PayTypeEnum):
        self.order_type = order_type
        self.config_cls = ChannelConfig if order_type == PayTypeEnum.DEPOSIT else ProxyChannelConfig
        self.cache = ChannelLimitCache(order_type.name)

    # @classmethod
    # def get_channel_min_max_list(cls, channels, test=False, client_ip=None):
    #     """
    #     获取已经排序的每个通道的最大最小限额列表
    #     :param channels:
    #     :param test:
    #     :param client_ip:
    #     :return:
    #     """
    #     limit_min_lst = []
    #     limit_max_lst = []
    #
    #     if not channels:
    #         return limit_min_lst, limit_max_lst
    #
    #     for channel in channels:
    #         # print(channel)
    #         if not channel.is_channel_valid(test, client_ip=client_ip):
    #             continue
    #
    #         # print(channel.limit_per_max)
    #         limit_min_lst.append(channel.limit_per_min)
    #         limit_max_lst.append(channel.limit_per_max)
    #
    #     limit_min_lst.sort()
    #     limit_max_lst.sort()
    #
    #     return limit_min_lst, limit_max_lst

    # def limit_min_max(self, channel_list, test):
    #     """
    #     遍历充值渠道 获取充值单笔交易限额 并排序
    #     :param channel_list:
    #     :param test:
    #     :return:
    #     """
    #     limit_min_lst, limit_max_lst = self.get_channel_min_max_list(channel_list, test)
    #
    #     if not limit_min_lst or not limit_max_lst:
    #         return None, None
    #
    #     # if self.order_type == PayTypeEnum.DEPOSIT:
    #     #     # 取所有最小限额的最大值，所有最大限额的最小值
    #     #     return limit_min_lst[-1], limit_max_lst[0]
    #     # else:
    #     #     # 提现整好反过来
    #     #     return limit_min_lst[0], limit_max_lst[-1]
    #     return limit_min_lst[0], limit_max_lst[-1]
    #
    # def sync_db_channels_to_cache(self):
    #     """
    #     同步db配置到缓存
    #     :return:
    #     """
    #     channels = self.config_cls.query_all()
    #     channels = self.config_cls.filter_latest_items(channels)
    #
    #     limit_min, limit_max = self.limit_min_max(channels, True)
    #
    #     if limit_min is None or limit_max is None:
    #         current_app.logger.error('没有可用的渠道配置, order_type: %s', self.order_type)
    #         return False
    #
    #     if not self.cache.set_limit(limit_min, limit_max):
    #         current_app.logger.error('缓存添加失败, order_type: %s, limit_min: %s, limit_max: %s',
    #                                  self.order_type, limit_min, limit_max)
    #         return False
    #
    #     return True

    # def get_channel_limit(self):
    #     """
    #     获取通道上下限金额
    #     :return:
    #     """
    #     limit_min, limit_max = self.cache.get_limit()
    #     if not limit_min and not limit_max:
    #
    #         if not self.sync_db_channels_to_cache():
    #             return 0, 0
    #
    #         limit_min, limit_max = self.cache.get_limit()
    #
    #     return limit_min, limit_max

    # def is_channel_amount_limit(self, amount):
    #     """
    #     判断金额是否超出通道限制
    #     :param amount:
    #     :return:
    #     """
    #     limit_min, limit_max = self.get_channel_limit()
    #     return amount < limit_min or amount > limit_max

    @classmethod
    def add_day_amount(cls, channel: ChannelConfigEnum, amount: Decimal):
        """
        增加通道的交易总额度
        :param channel:
        :param amount:
        :return:
        """
        ChannelDayLimitCache().incr_day_amount(channel, amount)
