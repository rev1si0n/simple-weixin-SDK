# encoding=utf-8

import pymysql
import pymysql.cursors

from .storage import SqlStorageBase
from ..utils import parse_rfc1738_args


class MySQLStorage(SqlStorageBase):

    def __init__(self, uri):
        params = parse_rfc1738_args(uri)
        del params['name']

        self.database = pymysql.connect(**params)

        def make_cursor(database):
            class MysqlCursor(pymysql.cursors.Cursor):

                def __exit__(self, *exc_info):
                    del exc_info
                    database.commit()
                    self.close()

            return MysqlCursor

        self.Cursor = make_cursor(self.database)
        self._create_table()

    def _create_table(self):
        """
        创建数据表
        """
        with self.database.cursor(self.Cursor) as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS `storage` (
                        `key` VARCHAR (128) NOT NULL,
                        `value` BLOB NULL,
                        `expired` BIGINT NULL,
                        PRIMARY KEY (`key`)
                ) DEFAULT CHARACTER SET = utf8mb4;""")

    def _translate_blob(self, data):
        """
        转义blob字段, pymysql直接返回二进制数据
        """
        return data

    def _escape_sql_args_formatter(self, statement):
        """
        转义sql语句中的参数格式化符号
        """
        return statement.replace("?", "%s")
