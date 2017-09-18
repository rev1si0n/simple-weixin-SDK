# encoding=utf-8
import redis

from ._base_ import _Storage_


class RedisStorage(_Storage_):

    def __init__(self, uri="redis://127.0.0.1/0"):
        """
        Redis 存储, 默认使用本机6379, 0号数据库
        """
        self.database = redis.StrictRedis.from_url(uri)

    def get(self, key, encoding=None):
        """
        get implemention for redis
        """
        result = self.database.get(key)

        result = self.unserialize(result, encoding=encoding)
        return result

    def set(self, key, pyobj, expires=86400, encoding="utf-8"):
        """
        set implemention for redis
        """
        data = self.serialize(pyobj, encoding=encoding)

        self.database.setex(key, expires, data)
        return

    def delete(self, key):
        """
        delete implemention for redis
        """
        self.database.delete(key)

    def purge_expired(self):
        """
        purge_expired implemention for redis
        """
        return

    def get_all_keys_by_wildcard(self, wildcard="*"):
        """
        get_all_by_wildcard implemention for redis
        """
        keys = self.database.keys(wildcard)

        mmp = map(lambda k: k.decode("utf-8"), keys)
        return list(mmp)

    def is_expired(self, key):
        """
        is_expired implemention for redis
        """
        return not self.database.exists(key)

    def get_ttl(self, key):
        """
        get_ttl implemention for redis
        """
        return self.database.ttl(key)
