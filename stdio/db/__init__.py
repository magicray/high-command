import sqlite3


class SQLite():
    def __init__(self, name):
        self.conn = None
        self.path = name + '.sqlite3'

    def __call__(self, query, *params):
        if self.conn is None:
            self.conn = sqlite3.connect(self.path)

        return self.conn.execute(query, params)

    def commit(self):
        if self.conn:
            self.conn.commit()
            self.conn.close()
            self.conn = None

    def __del__(self):
        if self.conn:
            self.conn.rollback()
            self.conn.close()
