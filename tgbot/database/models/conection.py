import sqlite3
from queue import Queue, Empty

DB_FILE = 'test.db'

class ConnectionPool:

    __instance = None

    def __init__(self, max_size=2, db_file=DB_FILE) -> None:
        self._max_size = max_size
        self._db = db_file
        self._pull = Queue(max_size)
        pass

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(ConnectionPool, *args, **kwargs)
        return cls.__instance

    def get_conn(self):
        try:
            return self._pull.get(block=False)
        except Empty:
            return sqlite3.connect(self._db)
    
    def put_conn(self, conn: sqlite3.Connection):
        if self._pull.qsize() < self._max_size:
            self._pull.put(conn, block=False)
        else:
            conn.close()

class ConectionController:
    def __init__(self, conn_pull = ConnectionPool()) -> None:
        self.conn_pull = conn_pull
        self.curent_conn = None
        pass

    def __enter__(self):
        self.conn = self.conn_pull.get_conn()
        return DBWorker(self.conn)
    
    def __exit__(self, exception_type, exception_value, traceback):
        self.conn_pull.put_conn(self.conn)


class DBWorker:

    def __init__(self, conn: sqlite3.Connection = ConnectionPool().get_conn()) -> None:
        self.conn = conn
        pass

    def __enter__(self):
        return self
    
    def __exit__(self, exception_type, exception_value, traceback, conn=None):
        self.put_conn(conn)

    def load_from_db(self, __id, __class):
        cur = self.conn.cursor()
        return __class.select_from_db(__id, cur)

    def load_all(self, __class):
        cur = self.conn.cursor()
        return __class.get_all(cur)
        
    def load_by_name(self, __name, __class):
        cur = self.conn.cursor()
        return __class.select_from_db_by_name(__name, cur)

    def load_previous(self, id_, __class):
        cur = self.conn.cursor()
        return __class.get_previous(id_, cur)
    
    def insert(self, __object):
        cur = self.conn.cursor()
        __object.insert_to_db(cur)