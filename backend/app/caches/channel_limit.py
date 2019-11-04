from decimal import Decimal

from app.caches.base import RedisHashCache
from app.caches.keys import CHANNEL_LIMIT_KEY_PREFIX, CHANNEL_DAY_LIMIT_KEY_PREFIX
from app.enums.channel import ChannelConfigEnum
from app.libs.balance_kit import BalanceKit
from app.libs.datetime_kit import DateTimeKit


class ChannelLimitCache(RedisHashCache):
    """
    通道每天上下限缓存
    """
    KEY_PREFIX = CHANNEL_LIMIT_KEY_PREFIX

    def __init__(self, name):
        super(ChannelLimitCache, self).__init__(suffix=name)

    def set_limit(self, limit_min, limit_max):
        data = dict(
            limit_min=str(limit_min),
            limit_max=str(limit_max),
        )
        return self.hmset(data)

    def get_limit(self):
        data = self.hgetall()
        if data:
            return Decimal(data[b'limit_min'].decode('utf8')), Decimal(data[b'limit_max'].decode('utf8'))

        return 0, 0


class ChannelDayLimitCache(RedisHashCache):
    """
    通道每天流水金额累积
    """
    KEY_PREFIX = CHANNEL_DAY_LIMIT_KEY_PREFIX

    def get_expiration(self):
        """
        过期时间为每天的午夜0点
        :return:
        """
        return DateTimeKit.gen_midnight_timestamp() - DateTimeKit.get_cur_timestamp()

    def incr_day_amount(self, channel: ChannelConfigEnum, value: Decimal):
        value = BalanceKit.multiple_hundred(value)
        ret = self.hincr(channel.name, value)
        self.update_expiration()
        return ret

    def get_day_amount(self, channel: ChannelConfigEnum):
        value = self.hget(channel.name)
        if not value:
            return 0

        value = int(value.decode('utf8'))
        return BalanceKit.divide_hundred(value)


if __name__ == "__main__":
    from app.main import flask_app
    from app.enums.trade import PayTypeEnum

    with flask_app.app_context():
        cache = ChannelLimitCache(PayTypeEnum.DEPOSIT.name)

        _limit_min = Decimal("500.11")
        _limit_max = Decimal("5000.55")

        cache.set_limit(_limit_min, _limit_max)
        x, y = cache.get_limit()

        assert _limit_min == x
        assert _limit_max == y

        cache = ChannelDayLimitCache()
        amount = Decimal("1000.28")
        v = cache.get_day_amount(ChannelConfigEnum.CHANNEL_1001)
        print(v)
        assert v == 0
        cache.incr_day_amount(ChannelConfigEnum.CHANNEL_1001, amount)
        v = cache.get_day_amount(ChannelConfigEnum.CHANNEL_1001)
        print(v)
        assert amount == v
        ttl = cache.get_ttl()
        print(ttl)
        assert ttl < 24 * 60 * 60
