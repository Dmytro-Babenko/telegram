import sqlite3 as sql3
from contextlib import contextmanager

DB_FILE = 'test.db'

@contextmanager
def create_connection(DB_FILE):
    conn = sql3.connect(DB_FILE)
    yield conn
    conn.rollback()
    conn.close()

