# encoding=utf-8
import redis

from .storage import StorageBase


class RedisStorage(StorageBase):

    def __init__(self, uri="redis://127.0.0.1/0"):
        self.database = redis.StrictRedis.from_url(uri)

    def get(self, key, encoding=None):
        result = self.database.get(key)

        result = self.unserialize(result, encoding=encoding)
        return result

    def set(self, key, pyobj, expires=86400, encoding="utf-8"):
        data = self.serialize(pyobj, encoding=encoding)

        self.database.setex(key, expires, data)
        return

    def delete(self, key):
        self.database.delete(key)

    def purge_expired(self):
        return

    def get_all_keys_by_wildcard(self, wildcard="*"):
        keys = self.database.keys(wildcard)

        mmp = map(lambda k: k.decode("utf-8"), keys)
        return list(mmp)

    def is_expired(self, key):
        return not self.database.exists(key)

    def get_ttl(self, key):
        return self.database.ttl(key)
