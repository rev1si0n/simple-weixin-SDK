# encoding=utf-8
import msgpack
from time import time as get_timestamp


class StorageBase(object):
    """
    存储基础类, 可以派生出其他存取类
    实质上是一个 key:value 存取器，标注NotImplementedError的需要自行实现
    """

    def get(self, key, encoding=None):
        """
        从数据库中读取key, 如果数据库中未找到会话信息则应返回 None
        encoding: 解码数据时指定编码, 因为可能存储的是binary数据, 所以默认不解码
        """
        raise NotImplementedError

    def set(self, key, pyobj, expires=86400, encoding="utf-8"):
        """
        保存key到数据库, 默认的存活时间为1天, 无返回值
        pyobj: 合法的Python常用类型
        expires: 存活时间
        encoding: 当存储数据存在字串时使用此编码对字串编码
        """
        raise NotImplementedError

    def delete(self, key):
        """
        从数据库删除key, 无返回值
        """
        raise NotImplementedError

    def purge_expired(self):
        """
        从数据库删除所有已过期会话, 无返回值, 像Redis这类无需清除过期key的数据库直接返回
        """
        raise NotImplementedError

    def get_all_keys_by_wildcard(self, wildcard="*"):
        """
        依据wildcard从数据库获取key, 返回key列表
        主要是用来获取微信客服会话未过期的会话
        如果无法实现则返回 []
        为了统一各个数据库, wildcard/通配符应该仅只支持
        ? : 单个任意字符
        * : 多个任意字符
        """
        raise NotImplementedError

    def is_expired(self, key):
        """
        判断key是否存在或已过期
        """
        raise NotImplementedError

    def get_ttl(self, key):
        """
        获取key的剩余存活秒数, 无法实现返回0, 不存在有效key返回-2
        """
        raise NotImplementedError

    def serialize(self, dict, encoding="utf-8"):
        """
        将key对应值转换成字节类型, 可以自行修改实现方法
        """
        bytes = msgpack.dumps(dict, encoding=encoding)
        return bytes

    def unserialize(self, byte, encoding=None):
        """
        将字节数据转换成Pyobj, 需与serialize统一
        """
        if not isinstance(byte, bytes):
            return

        dict = msgpack.loads(byte, encoding=encoding)
        return dict


class SqlStorageBase(StorageBase):

    def _translate_blob(self, data):
        """
        转义blob字段
        """
        raise NotImplementedError

    def _escape_sql_args_formatter(self, statement):
        """
        转义sql语句中的参数格式化符号
        """
        raise NotImplementedError

    def get(self, key, encoding=None):
        """
        Sqlite3, mysql 通用 get
        """
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
        """
        Sqlite3, mysql 通用 set
        """
        data = self.serialize(pyobj, encoding=encoding)
        with self.database.cursor(self.Cursor) as cursor:
            cursor.execute(self._escape_sql_args_formatter("""
                REPLACE INTO `storage`
                (`key`, `value`, `expired`)
                VALUES (?, ?, ?);"""),
            (key, self._translate_blob(data), get_timestamp() + expires))

    def delete(self, key):
        """
        Sqlite3, mysql 通用 delete
        """
        with self.database.cursor(self.Cursor) as cursor:
            cursor.execute(self._escape_sql_args_formatter("""
                DELETE
                FROM `storage`
                WHERE `key`=? LIMIT 1;"""),
                (key,))

    def purge_expired(self):
        """
        Sqlite3, mysql 通用 purge_expired
        """
        with self.database.cursor(self.Cursor) as cursor:
            cursor.execute(self._escape_sql_args_formatter("""
                DELETE
                FROM `storage`
                WHERE `expired`<=?;"""),
                (get_timestamp(),))

    def get_all_keys_by_wildcard(self, wildcard="*"):
        """
        Sqlite3, mysql 通用 get_all_keys_by_wildcard
        """
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
        """
        Sqlite3, mysql 通用 is_expired
        """
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
        """
        获取key的剩余存活秒数
        """
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
