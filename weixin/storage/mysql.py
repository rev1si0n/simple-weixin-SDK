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
        with self.database.cursor(self.Cursor) as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS `storage` (
                        `key` VARCHAR (128) NOT NULL,
                        `value` BLOB NULL,
                        `expired` BIGINT NULL,
                        PRIMARY KEY (`key`)
                ) DEFAULT CHARACTER SET = utf8mb4;""")

    def _translate_blob(self, data):
        return data

    def _escape_sql_args_formatter(self, statement):
        return statement.replace("?", "%s")
