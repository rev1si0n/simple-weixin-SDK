# encoding=utf-8
import msgpack
from time import time as get_timestamp


class _Storage_(object):
    """
    存储基础类, 可以派生出其他存取类
    实质上是一个 key:value 存取器，标注NotImplementedError的需要自行实现
    """

    def get(self, key, encoding=None):
        """
        从数据库中读取key, 如果数据库中未找到会话信息则应返回 None
        """
        raise NotImplementedError

    def set(self, key, pyobj, expires=86400, encoding="utf-8"):
        """
        保存key到数据库, 默认的存活时间为1天, 无返回值
        """
        raise NotImplementedError

    def delete(self, key):
        """
        从数据库删除key, 无返回值
        """
        raise NotImplementedError

    def purge_expired(self):
        """
        从数据库删除所有已过期会话
        """
        raise NotImplementedError

    def get_all_keys_by_wildcard(self, wildcard="*"):
        """
        从数据库获取所有以key_prefix为前缀且未过期的key
        主要是用来获取微信客服会话未过期的会话
        如果无法实现则返回 []
        为了同意各个数据库, wildcard/通配符应该仅只支持
        ? : 单个任意字符
        * : 多个任意字符
        """
        raise NotImplementedError

    def is_expired(self, key):
        """
        判断key是否已过期
        """
        raise NotImplementedError

    def serialize(self, dict, encoding="utf-8"):
        """
        将key值转换成字节类型
        """
        bytes = msgpack.dumps(dict, encoding=encoding)
        return bytes

    def unserialize(self, byte, encoding=None):
        """
        将字节数据转换成Pyobj
        """
        if not isinstance(byte, bytes):
            return
        
        dict = msgpack.loads(byte, encoding=encoding)
        return dict

    def _is_meaningful_value(self, v):
        """
        供get_or_set使用, 某些返回值不会被set
        """
        return all([
            v, isinstance(v, (bytes, str, dict, list))])

    def get_or_set(self, key, callback=None, expires=86400,
                            encoding=None,
                            **kwargs):
        """
        从数据库读取, 如果不存在则设置callback的返回值
        """
        result = self.get(key, encoding=encoding)
        if result is None:
            if callback:
                is_save = True
                if callable(callback):
                    result = callback(**kwargs)
                    if isinstance(result, tuple):
                        is_save, result = result
                else:
                    result = callback

                if not is_save or not self._is_meaningful_value(result):
                    # 符合要求的返回值才会被 set
                    # 像None, true,false这些会被丢弃
                    return result

                enc = encoding or "utf-8"
                self.set(key, result, expires=expires,
                             encoding=enc)

        return result


class _BaseSqlStorage_(_Storage_):

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
