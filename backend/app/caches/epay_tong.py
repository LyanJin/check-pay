from app.caches.base import RedisListCache
from app.caches.keys import EPAY_TONG_WITHDRAW_KEY_PREFIX


class EpayTongOrderCache(RedisListCache):
    KEY_PREFIX = EPAY_TONG_WITHDRAW_KEY_PREFIX

    def __init__(self):
        super(EpayTongOrderCache, self).__init__()
