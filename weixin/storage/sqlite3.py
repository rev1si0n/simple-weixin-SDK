# encoding=utf-8
import sqlite3

from .storage import SqlStorageBase


class Sqlite3Storage(SqlStorageBase):

    def __init__(self, uri="weixin.sqlite3"):

        self.database = sqlite3.connect(uri, check_same_thread=False)

        def make_cursor(database):
            class Sqlite3Cursor(sqlite3.Cursor):
                def __enter__(self):
                    return self

                def __exit__(self, *exc_info):
                    del exc_info
                    database.commit()
                    self.close()

            return Sqlite3Cursor

        self.Cursor = make_cursor(self.database)
        self._create_table()

    def _create_table(self):
        with self.database.cursor(self.Cursor) as cursor:
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS storage
            (
                key TEXT PRIMARY KEY NOT NULL,
                value BLOB NOT NULL,
                expired BIGINT DEFAULT 0
            );""")

    def _translate_blob(self, data):
        return memoryview(data)

    def _escape_sql_args_formatter(self, statement):
        return statement
