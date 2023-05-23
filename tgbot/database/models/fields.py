from abc import ABC, abstractmethod, abstractstaticmethod
from datetime import datetime
import sqlite3

# from tgbot.database.models.order_creator import OrderType, Subject, University

# from tgbot.database.models import Solutions, Files

class AbstractModel(ABC):
    def __init__(self) -> None:
        pass

    @abstractmethod
    def insert_to_db(self, cur):
        pass

    @abstractstaticmethod
    def select_from_db():
        pass

    @abstractstaticmethod
    def get_all():
        pass


class User(AbstractModel):
    _table = None

    def __init__(self, telegram_id, first_name, last_name=None, username=None, phone_num=None) -> None:
        self.telegram_id = telegram_id
        self.first_name = first_name
        self.last_name = last_name
        self.user_name = username
        self.phone = phone_num
        pass

    def insert_to_db(self, cur):
        insert_user = f"""INSERT INTO {self._table} (telegram_id, first_name, last_name, user_name, phone_number)
                            VALUES (?, ?, ?, ?, ?)"""
        values = (self.telegram_id, self.first_name, self.last_name, self.user_name, self.phone)
        cur.execute(insert_user, values) 

    @staticmethod
    def select_from_db(cls, telegram_id, cur):
        select_user = f'SELECT first_name, last_name, user_name, phone_number FROM {cls._table} WHERE telegram_id = ?'
        print(select_user)
        client_info = cur.execute(select_user, (telegram_id,)).fetchone()
        return cls(telegram_id, *client_info)
                
    @staticmethod
    def get_all(cls, cur):
        print('a')
        cur.row_factory = lambda cursor, row: row[0]
        sql = f'SELECT telegram_id FROM {cls._table}'
        return cur.execute(sql).fetchall()

class Admin(User):
    _table = 'admins'

    @staticmethod
    def get_all(cur):
        return User.get_all(__class__, cur)
    
    @staticmethod
    def select_from_db(telegram_id, cur):
        return User.select_from_db(__class__, telegram_id, cur)
    
class Client(User):
    _table = 'clients'

    @staticmethod
    def get_all(cur):
        return User.get_all(__class__, cur)
    
    @staticmethod
    def select_from_db(telegram_id, cur):
        return User.select_from_db(__class__, telegram_id, cur)

class Field(AbstractModel):
    _table = None
    _category_name = None
    _column = None

    def __init__(self, name: str, id_=None, **args) -> None:
        
        self.name = name.capitalize()
        self.id = id_

    def __str__(self):
        return self.name

    def __repr__(self) -> str:
        return str(self)

    def get_key(self):
        return self.id

    def insert_to_db(self, cur):
        insert_sql= f'INSERT INTO {self._table} (name) VALUES (?)'
        cur.execute(insert_sql, (self.name,))

    def show_info(self):
        characteristics = {
            'Категорія': self._category_name,
            'Id': self.id,
            'Назва': self.name,
        }
        return '\n'.join(f'{char}: {value}' for char, value in characteristics.items() if value)

    @staticmethod
    def select_from_db(_id, cur: sqlite3.Cursor, _class):
        cur.row_factory = lambda cursor, value: value[0]
        name = cur.execute(f'SELECT name FROM {_class._table} WHERE id = ?', (_id,)).fetchone()
        return _class(name, _id)

    @staticmethod
    def select_from_db_by_name(_name, cur:sqlite3.Cursor, _class):
        cur.row_factory = lambda cursor, value: value[0]
        _id = cur.execute(f'SELECT id FROM {_class._table} WHERE name = ?', (_name,)).fetchone()
        return _class(_name, _id)

    @staticmethod
    def get_all(table, cur: sqlite3.Cursor):
        cur.row_factory = lambda cursor, value: value[0]
        return cur.execute(f'SELECT name FROM {table}').fetchall()
    
    @staticmethod
    def get_previous(table, _column, _client_id, cur:sqlite3.Cursor):
        cur.row_factory = lambda cursor, value: value[0]
        sql_get_ids = f'SELECT DISTINCT {_column} FROM orders WHERE client_id = ?'
        return cur.execute(f'SELECT name FROM {table} WHERE id IN ({sql_get_ids})', (_client_id,)).fetchall()

    
class Subject(Field):
    _table = 'subjects'
    _category_name = 'Предмет'
    _column = 'subject_id'

    @staticmethod
    def get_all(cur: sqlite3.Cursor):
        return Field.get_all(Subject._table, cur)
    
    @staticmethod
    def get_previous(_client_id, cur: sqlite3.Cursor):
        return Field.get_previous(Subject._table, Subject._column, _client_id, cur)

    @staticmethod
    def select_from_db(_id, cur: sqlite3.Cursor):
        return Field.select_from_db(_id, cur, Subject)
    
    @staticmethod
    def select_from_db_by_name(_name, cur):
        return Field.select_from_db_by_name(_name, cur, Subject)

class University(Field):
    _table = 'universities'
    _category_name = 'Університет'
    _column = 'univ_id'

    @staticmethod
    def get_all(cur: sqlite3.Cursor):
        return Field.get_all(University._table, cur)
    
    @staticmethod
    def get_previous(_client_id, cur: sqlite3.Cursor):
        return Field.get_previous(University._table, University._column, _client_id, cur)
    
    @staticmethod
    def select_from_db(_id, cur: sqlite3.Cursor):
        if _id:
            return Field.select_from_db(_id, cur, University)
        return None
    
    @staticmethod
    def select_from_db_by_name(_name, cur):
        return Field.select_from_db_by_name(_name, cur, University)

class OrderType(Field):
    _table = 'types'
    _category_name = 'Тип роботи'
    _column = 'type_id'

    def __init__(self, name, kind, id_=None, **args) -> None:
        super().__init__(name, id_)
        self.__kind = None
        self.kind = kind
    
    @property
    def kind(self):
        return self.__kind
    
    @kind.setter
    def kind(self, new_kind: str):
        new_kind = new_kind.lower()
        if new_kind in ('оф', 'он'):
            self.__kind = new_kind
        else:
            raise ValueError('No such kind')
        
    def show_info(self):
        characteristics = {
            'Категорія': self._category_name,
            'Id': self.id,
            'Назва': self.name,
            'Тип': self.kind
        }
        return '\n'.join(f'{char}: {value}' for char, value in characteristics.items() if value)
    
    def insert_to_db(self, cur):
        insert_sql= f'INSERT INTO {self._table} (name, kind) VALUES (?, ?)'
        cur.execute(insert_sql, (self.name, self.kind))

        
    @staticmethod
    def select_from_db(__id, cur: sqlite3.Cursor):
        __name, __kind = cur.execute(f'SELECT name, kind FROM {OrderType._table} WHERE id = ?', (__id,)).fetchone()
        return OrderType(__name, __id, __kind)
    
    @staticmethod
    def select_from_db_by_name(__name, cur: sqlite3.Cursor):
        __id, __kind = cur.execute(f'SELECT id, kind FROM {OrderType._table} WHERE name = ?', (__name,)).fetchone()
        return OrderType(__name, __kind, __id)

    @staticmethod
    def get_all(cur: sqlite3.Cursor):
        return Field.get_all(OrderType._table, cur)
    
    @staticmethod
    def get_previous(_client_id, cur: sqlite3.Cursor):
        return Field.get_previous(OrderType._table, OrderType._column, _client_id, cur)
    
class OrderDate:
    _category_name = 'Дата та час'

    def __init__(self, value: datetime) -> None:
        self.value = value

    def __str__(self) -> str:
        return self.value.strftime('%d.%m.%y %H:%M')
    
    def __repr__(self) -> str:
        return str(self)
    
    def get_key(self):
        return self.value
    
    def set_time(self, time: datetime):
        self.value = datetime.combine(self.value, time)
    
class OrderTorV:
    _category_name = None

    def __init__(self, value: str = '') -> None:
        self.value = value

    def __str__(self) -> str:
        return self.value
    
    def __repr__(self) -> str:
        return str(self)
    
    def get_key(self):
        return self.value

class OrderTheme(OrderTorV):
    _category_name = 'Тема'

class OrderVar(OrderTorV):
    _category_name = 'Варіант'

if __name__ == '__main__':
    a = OrderDate(datetime(2000, 3, 1, 12, 0))
    print(a)
    time = datetime.strptime('23:00', '%H:%M').time()
    a.set_time(time)
    print(a)