from collections import UserList, UserString, defaultdict
from datetime import datetime
import sqlite3

from aiogram import types, Bot
from aiogram.types.document import Document

# from tgbot.texts.texts import PHOTO_EXTENSION
# from tgbot.database.data import DB_FILE

PHOTO_EXTENSION=''
DB_FILE = 'test.db'

class Loader:
    db = DB_FILE

    # def __init__(self, db) -> None:
    #     self.db = db
    #     pass

    @staticmethod
    def load_from_db(__id, __class):
        with sqlite3.connect(Loader.db) as con:
            cur = con.cursor()
            return __class.select_from_db(__id, cur)

    @staticmethod
    def load_all(__class):
        with sqlite3.connect(Loader.db) as con:
            cur = con.cursor()
            return __class.get_all(cur)
        
    @staticmethod
    def load_by_name(__name, __class):
        with sqlite3.connect(Loader.db) as con:
            cur = con.cursor()
            return __class.select_from_db_by_name(__name, cur)

    @staticmethod
    def load_previous(id_, __class):
        with sqlite3.connect(Loader.db) as con:
            cur = con.cursor()
            return __class.get_previous(id_, cur)


class AbstractModel:
    def __init__(self) -> None:
        pass

    def insert_to_db(self):
        pass

    @staticmethod
    def select_from_db():
        pass 

class Field(AbstractModel):
    _table = None
    _category_name = None

    def __init__(self, name: str, id_=None, **args) -> None:
        
        self.name = name.capitalize()
        self.id = id_

    def __repr__(self) -> str:
        return self.name

    def insert_to_db(self):
        with sqlite3.connect(DB_FILE) as con:
            cur = con.cursor()
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
    def get_previous(table, id_, cur:sqlite3.Cursor):
        cur.row_factory = lambda cursor, value: value[0]
        return cur.execute(f'SELECT name FROM {table} WHERE id = ?', (id_,)).fetchall()
    
class Subject(Field):
    _table = 'subjects'
    _category_name = 'Предмет'

    @staticmethod
    def get_all(cur: sqlite3.Cursor):
        return Field.get_all(Subject._table, cur)
    
    @staticmethod
    def get_previous(id_, cur: sqlite3.Cursor):
        return Field.get_previous(Subject._table, id_, cur)

    @staticmethod
    def select_from_db(_id, cur: sqlite3.Cursor):
        return Field.select_from_db(_id, cur, Subject)
    
    @staticmethod
    def select_from_db_by_name(_name, cur):
        return Field.select_from_db_by_name(_name, cur, Subject)

class University(Field):
    _table = 'universities'
    _category_name = 'Університет'

    @staticmethod
    def get_all(cur: sqlite3.Cursor):
        return Field.get_all(University._table, cur)
    
    @staticmethod
    def get_previous(id_, cur: sqlite3.Cursor):
        return Field.get_previous(University._table, id_, cur)
    
    @staticmethod
    def select_from_db(_id, cur: sqlite3.Cursor):
        return Field.select_from_db(_id, cur, University)
    
    @staticmethod
    def select_from_db_by_name(_name, cur):
        return Field.select_from_db_by_name(_name, cur, University)

class OrderType(Field):
    _table = 'types'
    _category_name = 'Тип роботи'

    def __init__(self, name, kind, id_=None, **args) -> None:
        super().__init__(name, id_)
        self.__kind = None
        self.kind = kind
        print(self.kind)
    
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
    
    def insert_to_db(self):
        with sqlite3.connect(DB_FILE) as con:
            cur = con.cursor()
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

    # def select_kind(self, cur: sqlite3.Cursor):
    #     cur.row_factory = lambda cursor, value: value[0]
    #     if self.id:
    #         return cur.execute(f'SELECT kind FROM {self.__table} WHERE id = ?', (self.id,)).fetchone()
    #     return cur.execute(f'SELECT kind FROM {self.__table} WHERE name = ?', (self.name,)).fetchone()

    @staticmethod
    def get_all(cur: sqlite3.Cursor):
        return Field.get_all(OrderType._table, cur)
    
    @staticmethod
    def get_previous(id_, cur: sqlite3.Cursor):
        return Field.get_previous(OrderType._table, id_, cur)
        
class Admin(AbstractModel):
    
    @staticmethod
    def get_all(cur):
        cur.row_factory = lambda cursor, row: row[0]
        sql = 'SELECT telegram_id FROM admins'
        return cur.execute(sql).fetchall()

class Client(AbstractModel):
    def __init__(self, telegram_id, first_name, last_name=None, username=None, phone_num=None) -> None:
        self.telegram_id = telegram_id
        self.first_name = first_name
        self.last_name = last_name
        self.user_name = username
        self.phone = phone_num
        pass

    def insert_to_db(self):
        with sqlite3.connect(DB_FILE) as con:
            cur = con.cursor()
            insert_client = """INSERT INTO clients(telegram_id, first_name, last_name, user_name, phone_number)
                                VALUES (?, ?, ?, ?, ?)"""
            values = (self.telegram_id, self.first_name, self.last_name, self.user_name, self.phone)
            print(values)
            cur.execute(insert_client, values)    

    @staticmethod
    def select_from_db(telegram_id, cur):
        select_client = 'SELECT first_name, last_name, user_name, phone_number FROM clients WHERE telegram_id = ?'
        client_info = cur.execute(select_client, (telegram_id,)).fetchone()
        return Client(telegram_id, *client_info)
                
    @staticmethod
    def get_all(cur):
        cur.row_factory = lambda cursor, row: row[0]
        sql = 'SELECT telegram_id FROM clients'
        return cur.execute(sql).fetchall()

class Order(AbstractModel):
    def __init__(self, client:Client, type_order: OrderType, subject: Subject, date_time:datetime, t_or_v:str, 
                 university:University=None, order_id:int=None, task_files=None, 
                 solutions=None, **kwargs) -> None:
        self.order_id = order_id
        self.client = client
        self.type_order = type_order
        self.subject = subject
        self.datetime = date_time
        self.t_or_v = t_or_v
        self.university = university
        self.task_files:Files = task_files
        self.solutions:Solutions = solutions

    def form_description(self):
        points = ('Тип', 'Предмет', 'Дата та час', 'Тема' if self.type_order.kind == 'оф' else 'Варіант')
        values = (self.type_order, self.subject, self.datetime, self.t_or_v)
        return '\n'.join(f'{point}: {value}' for point, value in zip(points, values))        

    def insert_to_db(self):

        with sqlite3.connect(DB_FILE) as con:
            con.row_factory = lambda cursor, row: row[0]
            cur = con.cursor()

            insert_order = """INSERT INTO orders (client_id, type_id, subject_id, order_date, univ_id, theme_or_variant)
                            VALUES (?, ?, ?, ?, ?, ?) """
            values = (self.client.telegram_id, self.type_order.id, self.subject.id, 
                      self.datetime, self.university.id, self.t_or_v)
            cur.execute(insert_order, values)
            self.order_id = cur.lastrowid

            self.task_files.insert_to_db(self.order_id, cur, 'task')
            self.solutions.insert_to_db(self.order_id, cur)

    # @staticmethod
    # def get_kind(order_type):
    #     with sqlite3.connect(DB_FILE) as con:
    #         con.row_factory = lambda cursor, row: row[0]
    #         cur = con.cursor()
    #         select_kind = 'SELECT kind FROM types WHERE name = ?'
    #         order_kind = cur.execute(select_kind, (order_type,)).fetchone()
    #         return order_kind
        
    @staticmethod
    def select_from_db(order_id, cur):

        # def select_name(table_name, id):
        #     return cur.execute(f'SELECT id FROM {table_name} WHERE name = ?', (id,)).fetchone()
        
        sql_select_order = """SELECT client_id, type_id, subject_id, order_date, univ_id, theme_or_variant 
                            FROM orders
                            WHERE id = ?"""
        
        client_id, type_id, subject_id, order_date, univ_id, theme_or_variant = cur.execute(sql_select_order,
                                                                                            (order_id,)).fetchone()
        
        order_client = Client.select_from_db(client_id, cur)  
        order_type = OrderType.select_from_db(type_id, cur)
        order_subject = Subject.select_from_db(subject_id, cur)
        order_univ = University.select_from_db(univ_id, cur) if univ_id else None

        order = Order(
            client=order_client,
            order_id=order_id,
            type_order=order_type,
            subject=order_subject,
            datetime=order_date,
            t_or_v=theme_or_variant,
            university=order_univ,
            date_time=order_date
        )

        order.task_files = Files()
        order.task_files.add_from_db(order_id, 'task', cur)

        order.solutions = Solutions(Files)
        order.solutions.add_from_db(order_id, cur)          
        return order
    
            
def file_group_checking(group_type):
    def decorator(func):
        def inner(self, lst: list, *args):
            if not (lst and isinstance(lst[-1], group_type) and lst[-1].checking_size(self)):
                lst.append(group_type())
            func(self, lst, *args)
        return inner
    return decorator

class CustomMediaGroup(UserList):
    async def sending(self, bot:Bot, chat_id):
        await bot.send_media_group(chat_id, self.data)

    def checking_size(self, *args):
        return len(self) < 10

class DocGroup(CustomMediaGroup):
    pass

class PhotoGroup(CustomMediaGroup):
    pass

class TextGroup(UserList):

    async def sending(self, bot:Bot, chat_id):
        for text in self:
            await bot.send_message(chat_id, text.data)

    def checking_size(self, new_element):
        return len(new_element) + len(self) <= 4096 - 2

class FileElement:
    def adding(self, lst: list):
        lst[-1].append(self)

    def insert_to_db(self):
        pass

class PhotoElement(types.InputMediaPhoto, FileElement):
    def __init__(self, *args, extension=PHOTO_EXTENSION, **kwargs):
        super().__init__(*args, **kwargs)
        self.extension = extension

    @file_group_checking(PhotoGroup)
    def adding(self, lst: list):
        super().adding(lst)

    def insert_to_db(self, order_id, file_number, file_group, cur:sqlite3.Cursor=None):
        sql = """INSERT into photos (telegram_id, pos, file_group, order_id)
                VALUES (?, ?, ?, ?)"""
        values = (self.media, file_number, file_group, order_id)

        if cur:
            cur.execute(sql, values)
        
        # with sqlite3.connect(DB_FILE) as con:
        #     cur = con.cursor()
        #     cur.execute(sql, values)

class DocElement(types.InputMediaDocument, FileElement):
    def __init__(self, extension, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.extension = extension

    @file_group_checking(DocGroup)
    def adding(self, lst: list[list]):
        super().adding(lst)

    def insert_to_db(self, order_id, file_number, file_group, cur:sqlite3.Cursor=None):
        sql = """INSERT into documents (telegram_id, pos, file_group, order_id)
                VALUES (?, ?, ?, ?)"""
        values = (self.media, file_number, file_group, order_id)

        if cur:
            cur.execute(sql, values)
            return None
        
        # with sqlite3.connect(DB_FILE) as con:
        #     cur = con.cursor()
        #     cur.execute(sql, values)

class TextElement(FileElement, UserString):

    @file_group_checking(TextGroup)
    def adding(self, lst: list):
        text_group: TextGroup = lst[-1]
        if text_group:
            text_group[-1].data += f'\n\n{self}'
        else:
            text_group.append(self)

    def insert_to_db(self, order_id, file_number, file_group, cur):
        sql = """INSERT into texts (text_info, pos, file_group, order_id)
                VALUES (?, ?, ?, ?)"""
        values = (self.data, file_number, file_group, order_id)
        cur.execute(sql, values)
    
class Files(UserList):

    def iter_all(self):
        for media_group in self:
            for media in media_group:
                yield media

    def add_element(self, element:DocElement|PhotoElement|TextElement):
        element.adding(self)

    def add_elements(self, lst):
        for element in lst:
            self.add_element(element)

    async def send_files(self, bot:Bot, chat_id):
        for group in self:
            group: DocGroup|PhotoGroup|TextGroup
            await group.sending(bot, chat_id)

    async def answer_files(self, message: types.Message):
        await self.send_files(message.bot, message.chat.id)

    def insert_to_db(self, order_id, cur, file_group):
        for i, element in enumerate(self.iter_all(), 1):
            element: PhotoElement|TextElement|DocElement
            element.insert_to_db(order_id, i, file_group, cur)

    def add_from_db(self, order_id, file_group, cur: sqlite3.Cursor):
        cur.row_factory = None
        photos = cur.execute('SELECT pos, telegram_id FROM photos WHERE order_id = ? AND file_group = ?',
                             (order_id, file_group)).fetchall()
        photo_dct = {pos: PhotoElement(media=telegram_id) for pos, telegram_id in photos}
        
        documents = cur.execute('SELECT pos, telegram_id FROM documents WHERE order_id = ? AND file_group = ?',
                             (order_id, file_group)).fetchall()
        doc_dct = {pos: DocElement(media=telegram_id, extension='doc') for pos, telegram_id in documents}
        
        texts = cur.execute('SELECT pos, text_info FROM texts WHERE order_id = ? AND file_group = ?',
                             (order_id, file_group)).fetchall()
        texts_dct = {pos: TextElement(text_info) for pos, text_info in texts}

        elements = dict(sorted({**photo_dct, **doc_dct, **texts_dct}.items())).values()
        self.add_elements(elements)

class Solutions(defaultdict):

    async def send_solutions(self, bot: Bot, chat_id):
        for num, files in self.items():
            if num:
                await bot.send_message(chat_id, num)
            files: Files
            await files.send_files(bot, chat_id)

    async def answer_solutions(self, message: types.Message):
        await self.send_solutions(message.bot, message.chat.id)

    def insert_to_db(self, order_id, cur):
        for task_num, files in self.items():
            files: Files
            files.insert_to_db(order_id, cur, task_num)


    def add_from_db(self, order_id, cur: sqlite3.Cursor):
        sql_select_fgr = '''SELECT file_group FROM (SELECT DISTINCT file_group, order_id FROM texts t 
                            UNION
                            SELECT DISTINCT file_group, order_id FROM photos p 
                            UNION
                            SELECT DISTINCT file_group, order_id FROM documents d)
                            WHERE file_group != 'task' AND order_id = ?
                            ORDER BY file_group '''
        
        cur.row_factory = lambda cursor, x: x[0]
        task_nums = cur.execute(sql_select_fgr, (order_id,)).fetchall()
        for num in task_nums:
            self[num].add_from_db(order_id, num, cur)



if __name__ == '__main__':
    a = Loader.load_from_db(2, Order)
    print(a.subject)
        
