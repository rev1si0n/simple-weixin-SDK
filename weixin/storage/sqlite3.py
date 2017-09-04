# encoding=utf-8
import sqlite3

from ._base_ import _BaseSqlStorage_


class Sqlite3Storage(_BaseSqlStorage_):

    def __init__(self, uri="weixin.sqlite3"):
        
        self.database = sqlite3.connect(uri, check_same_thread=False)
    
        def make_cursor(database):
            class Sqlite3Cursor(sqlite3.Cursor):
                def __enter__(self):
                    return self

                def __exit__(self, *exc_info):
                    """
                    自动提交
                    """
                    del exc_info
                    database.commit()
                    self.close()
            
            return Sqlite3Cursor

        self.Cursor = make_cursor(self.database)
        self._create_table()

    def _create_table(self):
        """
        创建数据表
        """
        with self.database.cursor(self.Cursor) as cursor:
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS storage
            (
                key TEXT PRIMARY KEY NOT NULL,
                value BLOB NOT NULL,
                expired BIGINT DEFAULT 0
            );""")

    def _translate_blob(self, data):
        """
        转义blob字段, sqlite3
        """
        return memoryview(data)

    def _escape_sql_args_formatter(self, statement):
        """
        转义sql语句中的参数格式化符号
        """
        return statement
 
