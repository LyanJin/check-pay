from app.caches.base import RedisHashCache
from app.caches.keys import USER_FLAG_CACHE_KEY_PREFIX
from app.enums.account import AccountFlagEnum


class UserFlagCache(RedisHashCache):
    """
    用户标签缓存
    """
    KEY_PREFIX = USER_FLAG_CACHE_KEY_PREFIX

    def __init__(self, uid):
        self.uid = uid
        super(UserFlagCache, self).__init__()

    def set_flag(self, flag: AccountFlagEnum):
        return self.hset(self.uid, flag.value)

    def get_flag(self):
        value = self.hget(self.uid)
        if not value:
            return None
        return AccountFlagEnum(int(value))


if __name__ == '__main__':
    from app.main import flask_app

    with flask_app.app_context():
        uid = 1
        UserFlagCache(uid).set_flag(AccountFlagEnum.VIP)
        flag = UserFlagCache(uid).get_flag()
        print(flag)
