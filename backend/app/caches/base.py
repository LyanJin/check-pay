"""
缓存基类，实现一些通用的缓存逻辑封装
"""
import json

from app.extensions import redis


class RedisCacheBase:
    CACHE_STORAGE = redis
    EXPIRATION = 60
    SERIALIZER = json
    KEY_PREFIX = ""
    KEY_SUFFIX = ""

    def __init__(self, prefix=None, suffix=None):
        self.prefix = prefix or self.KEY_PREFIX
        self.suffix = suffix or self.KEY_SUFFIX

    def get_cache_key(self, prefix=None, suffix=None):
        return self.join_key(prefix or self.prefix, suffix or self.suffix)

    @classmethod
    def split_key(cls, key):
        return key.split(":")

    @classmethod
    def join_key(cls, prefix, suffix):
        return "{}:{}".format(prefix, suffix)

    @classmethod
    def join_str(cls, *args):
        return '|'.join(map(str, args))

    @classmethod
    def get_key_suffix(cls, key):
        return cls.split_key(key)[1]

    @classmethod
    def get_key_prefix(cls, key):
        return cls.split_key(key)[0]

    def get_expiration(self):
        return self.EXPIRATION or 0

    def dumps(self, data):
        """
        缓存数据
        :param data:
        :return:
        """
        NotImplemented

    def loads(self):
        """
        加载数据
        :return:
        """
        NotImplemented

    def is_exist(self):
        """
        判断缓存是否存在
        :return:
        """
        return self.CACHE_STORAGE.exists(self.get_cache_key())

    def delete(self):
        """
        删除缓存
        :return:
        """
        self.CACHE_STORAGE.delete(self.get_cache_key())

    @classmethod
    def scan_iter(cls, prefix, suffix="*"):
        """
        根据suffix模式迭代出 key，非阻塞
        :param prefix:
        :param suffix:
        :return:
        """
        for key in cls.CACHE_STORAGE.scan_iter(cls.join_key(prefix, suffix)):
            yield key

    @classmethod
    def delete_key(cls, key):
        """
        删除key
        :param key:
        :return:
        """
        cls.CACHE_STORAGE.delete(key)

    def delete_cache(self):
        """
        删除缓缓存
        :return:
        """
        self.CACHE_STORAGE.delete(self.get_cache_key())

    def get_ttl(self):
        """
        获取key的有效期剩余时间
        :return:
        """
        return self.CACHE_STORAGE.ttl(self.get_cache_key())

    def incr(self):
        """
        将数据 +1
        :return:
        """
        return self.CACHE_STORAGE.incr(self.get_cache_key())

    def update_expiration(self, ttl=None):
        """
        更新有效时间
        :return:
        """
        exp = ttl or self.get_expiration()
        if exp:
            self.CACHE_STORAGE.expire(self.get_cache_key(), exp)


class RedisStringCache(RedisCacheBase):

    def __init__(self, prefix=None, suffix=None):
        super(RedisStringCache, self).__init__(prefix, suffix)

    def dumps(self, data):
        """
        缓存数据
        :param data:
        :return:
        """
        if self.SERIALIZER:
            data = self.SERIALIZER.dumps(data)

        exp = self.get_expiration()
        if exp > 0:
            return self.CACHE_STORAGE.setex(self.get_cache_key(), exp, data)
        else:
            return self.CACHE_STORAGE.set(self.get_cache_key(), data)

    def loads(self):
        """
        加载数据
        :return:
        """
        data = self.CACHE_STORAGE.get(self.get_cache_key())
        if not data:
            return None

        if self.SERIALIZER:
            data = self.SERIALIZER.loads(data)

        return data


class RedisHashCache(RedisCacheBase):

    def __init__(self, prefix=None, suffix=None):
        super(RedisHashCache, self).__init__(prefix, suffix)

    def hmset(self, data):
        """
        hset()
        :param data:
        :return:
        """
        data = self.CACHE_STORAGE.hmset(name=self.get_cache_key(), mapping=data)
        if not data:
            return None
        return data

    def hmget(self, keys):
        """

        :return:
        """
        data = self.CACHE_STORAGE.hmget(self.get_cache_key(), keys=keys)
        return data

    def hset(self, key, value):
        """

        :param key:
        :param value:
        :return:
        """
        data = self.CACHE_STORAGE.hset(name=self.get_cache_key(), key=key, value=value)
        if not data:
            return None
        return data

    def hget(self, key):
        """
        hget()
        :return:
        """
        return self.CACHE_STORAGE.hget(name=self.get_cache_key(), key=key)

    def hgetall(self):
        """
        返回字典
        :return:
        """
        return self.CACHE_STORAGE.hgetall(name=self.get_cache_key())

    def hincr(self, key, amount=1):
        """
        原子+操作
        :return:
        """
        return self.CACHE_STORAGE.hincrby(name=self.get_cache_key(), key=key, amount=amount)


class RedisListCache(RedisCacheBase):

    def __init__(self, prefix=None, suffix=None):
        super(RedisListCache, self).__init__(prefix, suffix)

    def lpush(self, value=None):
        return self.CACHE_STORAGE.lpush(self.get_cache_key(), value)

    def rpop(self):
        return self.CACHE_STORAGE.rpop(name=self.get_cache_key())

    def iter_list(self):
        length = self.CACHE_STORAGE.llen(self.get_cache_key())
        for _ in range(length):
            yield self.rpop()
