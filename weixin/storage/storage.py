# encoding=utf-8
import msgpack
from time import time as get_timestamp


class StorageBase(object):

    def get(self, key, encoding=None):
        raise NotImplementedError

    def set(self, key, pyobj, expires=86400, encoding="utf-8"):
        raise NotImplementedError

    def delete(self, key):
        raise NotImplementedError

    def purge_expired(self):
        raise NotImplementedError

    def get_all_keys_by_wildcard(self, wildcard="*"):
        raise NotImplementedError

    def is_expired(self, key):
        raise NotImplementedError

    def get_ttl(self, key):
        raise NotImplementedError

    def serialize(self, dict, encoding="utf-8"):
        bytes = msgpack.dumps(dict, encoding=encoding)
        return bytes

    def unserialize(self, byte, encoding=None):
        if not isinstance(byte, bytes):
            return
        dict = msgpack.loads(byte, encoding=encoding)
        return dict


class SqlStorageBase(StorageBase):

    def _translate_blob(self, data):
        raise NotImplementedError

    def _escape_sql_args_formatter(self, statement):
        raise NotImplementedError

    def get(self, key, encoding=None):
        with self.database.cursor(self.Cursor) as cursor:
            cursor.execute(self._escape_sql_args_formatter("""
                SELECT `value`
                FROM `storage`
                WHERE `key`=? AND `expired`>?
                LIMIT 1;"""),
            (key, get_timestamp()))

            result = cursor.fetchone()

        if not result:
            return

        t = result[0]
        t = self.unserialize(t, encoding=encoding)
        return t

    def set(self, key, pyobj, expires=86400, encoding="utf-8"):
        data = self.serialize(pyobj, encoding=encoding)
        with self.database.cursor(self.Cursor) as cursor:
            cursor.execute(self._escape_sql_args_formatter("""
                REPLACE INTO `storage`
                (`key`, `value`, `expired`)
                VALUES (?, ?, ?);"""),
            (key, self._translate_blob(data), get_timestamp() + expires))

    def delete(self, key):
        with self.database.cursor(self.Cursor) as cursor:
            cursor.execute(self._escape_sql_args_formatter("""
                DELETE
                FROM `storage`
                WHERE `key`=?;"""),
                (key,))

    def purge_expired(self):
        with self.database.cursor(self.Cursor) as cursor:
            cursor.execute(self._escape_sql_args_formatter("""
                DELETE
                FROM `storage`
                WHERE `expired`<=?;"""),
                (get_timestamp(),))

    def get_all_keys_by_wildcard(self, wildcard="*"):
        wc = wildcard.replace("*", "%").replace("?", "_")
        with self.database.cursor(self.Cursor) as cursor:
            cursor.execute(self._escape_sql_args_formatter("""
                SELECT `key`
                FROM `storage`
                WHERE `expired`>? AND `key` LIKE ?;"""),
                (get_timestamp(), wc))

            result = [k for k, *_ in cursor.fetchall()]

        return result

    def is_expired(self, key):
        with self.database.cursor(self.Cursor) as cursor:
            cursor.execute(self._escape_sql_args_formatter("""
                SELECT 1
                FROM `storage`
                WHERE `key`=? AND `expired`>?
                LIMIT 1;"""),
                (key, get_timestamp()))

            result = not bool(cursor.fetchone())

        return result

    def get_ttl(self, key):
        with self.database.cursor(self.Cursor) as cursor:
            cursor.execute(self._escape_sql_args_formatter("""
                SELECT `expired`
                FROM `storage`
                WHERE `key`=? AND `expired`>?
                LIMIT 1;"""),
                (key, get_timestamp()))
            result = cursor.fetchone()

        if not result: return -2
        
        ttl = int(result[0]) - get_timestamp()
        return int(ttl)
