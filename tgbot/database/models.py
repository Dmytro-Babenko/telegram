from collections import UserList, UserString, defaultdict
from datetime import datetime
import sqlite3

from aiogram import types, Bot
from aiogram.types.document import Document

# from tgbot.texts.texts import PHOTO_EXTENSION
# from tgbot.database.data import DB_FILE

PHOTO_EXTENSION=''
DB_FILE = 'test.db'

class AbstractModel:
    def __init__(self) -> None:
        pass

    def insert_to_db(self):
        pass

    @staticmethod
    def select_from_db():
        pass 

class Field(AbstractModel):
    __table = None

    def __init__(self, name=None, id_=None) -> None:

        if name == id_ == None:
            raise ValueError('Id or name')
        
        self.name = name
        self.id = id_

    def insert_to_db(self):
        with sqlite3.connect(DB_FILE) as con:
            cur = con.cursor()
            insert_sql= f'INSERT INTO {self.__table} (name) VALUES (?)'
            cur.execute(insert_sql, (self.name,))

    def select_id(self, cur):
        cur.row_factory = lambda cursor, value: value[0]
        self.id = cur.execute(f'SELECT id FROM {self.__table} WHERE name = ?', (self.name,)).fetchone()

    def select_name(self, cur):
        cur.row_factory = lambda cursor, value: value[0]
        self.name = cur.execute(f'SELECT name FROM {self.__table} WHERE id = ?', (self.id,)).fetchone()

    @staticmethod
    def get_all_names(table, cur: sqlite3.Cursor):
        cur.row_factory = lambda cursor, value: value[0]
        return cur.execute(f'SELECT name FROM {table}').fetchall()
    
class Subject(Field):
    __table = 'subjects'

    @staticmethod
    def get_all_names(cur: sqlite3.Cursor):
        return super().get_all_names(Subject.__table, cur)

class University(Field):
    __table = 'universities'

    @staticmethod
    def get_all_names(cur: sqlite3.Cursor):
        return super().get_all_names(University.__table, cur)
    
class Type(Field):
    __table = 'types'

    def __init__(self, name=None, id_=None, kind=None) -> None:
        super().__init__(name, id_)
        self.__kind = None
        self.kind = kind

    @property
    def kind(self):
        return self.__kind
    
    @kind.setter
    def kind(self, new_kind):
        if new_kind in ('оф', 'он'):
            self.__kind = new_kind

    def select_kind(self, cur: sqlite3.Cursor):
        cur.row_factory = lambda cursor, value: value[0]
        if self.id:
            return cur.execute(f'SELECT kind FROM {self.__table} WHERE id = ?', (self.id,)).fetchone()
        return cur.execute(f'SELECT kind FROM {self.__table} WHERE name = ?', (self.name,)).fetchone()

    @staticmethod
    def get_all_names(cur: sqlite3.Cursor):
        return super().get_all_names(Type.__table, cur)
        

class Admin(AbstractModel):
    
    @staticmethod
    def get_all_ids():
        with sqlite3.connect(DB_FILE) as con:
            con.row_factory = lambda cursor, row: row[0]
            cur = con.cursor()
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
    def select_from_db(telegram_id):
        with sqlite3.connect(DB_FILE) as con:
            cur = con.cursor()
            select_client = 'SELECT first_name, last_name, user_name, phone_number FROM clients WHERE telegram_id = ?'
            client_info = cur.execute(select_client, (telegram_id,)).fetchone()
        return Client(telegram_id, *client_info)
                
    @staticmethod
    def get_all_ids():
        with sqlite3.connect(DB_FILE) as con:
            con.row_factory = lambda cursor, row: row[0]
            cur = con.cursor()
            sql = 'SELECT telegram_id FROM clients'
            return cur.execute(sql).fetchall()

class Order(AbstractModel):
    def __init__(self, client:Client, type_order: Type, subject: Subject, date_time:datetime, t_or_v:str, 
                 kind_order ,university:University=None, order_id:int=None, task_files=None, 
                 solutions=None, **kwargs) -> None:
        self.order_id = order_id
        self.client = client
        self.type_order = type_order
        self.subject = subject
        self.datetime = date_time
        self.t_or_v = t_or_v
        self.university = university
        self.kind = kind_order
        self.task_files:Files = task_files
        self.solutions:Solutions = solutions

    def form_description(self):
        points = ('Тип', 'Предмет', 'Дата та час', 'Тема' if self.kind == 'оф' else 'Варіант')
        values = (self.type_order, self.subject, self.datetime, self.t_or_v)
        return '\n'.join(f'{point}: {value}' for point, value in zip(points, values))        

    def insert_to_db(self):
        
        def select_id(table_name, name):
            return cur.execute(f'SELECT id FROM {table_name} WHERE name = ?', (name,)).fetchone()
        
        with sqlite3.connect(DB_FILE) as con:
            con.row_factory = lambda cursor, row: row[0]
            cur = con.cursor()

            self.type_order.select_id(cur)
            self.subject.select_id(cur)
            if self.university:          
                self.university.select_id(cur)
            type_id = select_id('types', self.type_order)
            subject_id = select_id('subjects', self.subject)
            univ_id = select_id('universities', self.university)

            insert_order = """INSERT INTO orders (client_id, type_id, subject_id, order_date, univ_id, theme_or_variant)
                            VALUES (?, ?, ?, ?, ?, ?) """
            values = (self.client.telegram_id, type_id, subject_id, self.datetime, univ_id, self.t_or_v)
            cur.execute(insert_order, values)
            self.order_id = cur.lastrowid

            self.task_files.insert_to_db(self.order_id, cur, 'task')
            self.solutions.insert_to_db(self.order_id, cur)

    @staticmethod
    def get_kind(order_type):
        with sqlite3.connect(DB_FILE) as con:
            con.row_factory = lambda cursor, row: row[0]
            cur = con.cursor()
            select_kind = 'SELECT kind FROM types WHERE name = ?'
            order_kind = cur.execute(select_kind, (order_type,)).fetchone()
            return order_kind
        
    @staticmethod
    def select_from_db(order_id):

        def select_name(table_name, id):
            return cur.execute(f'SELECT id FROM {table_name} WHERE name = ?', (id,)).fetchone()
        
        sql_select_order = """SELECT client_id, type_id, subject_id, order_date, univ_id, theme_or_variant 
                            FROM orders
                            WHERE id = ?"""
        

        with sqlite3.connect(DB_FILE) as con:
            # con.row_factory = lambda cursor, row: row[0]
            cur = con.cursor()
            client_id, type_id, subject_id, order_date, univ_id, theme_or_variant = cur.execute(sql_select_order,
                                                                                                (order_id,)).fetchone()
            order_type = select_name('types', type_id)
            order_subject = select_name('subjects', subject_id)
            order_univ = select_name('universities', univ_id)

            order = Order(
                type_order=order_type,
                subject=order_subject,
                datetime=order_date,
                t_or_v=theme_or_variant,
                university=order_univ,
                kind_order='он'
            )

            order.order_id = order_id

            order.task_files = Files()
            order.task_files.add_from_db(order_id, 'task', cur)

            order.solutions = Solutions(Files)
            order.solutions.add_from_db(order_id, cur)

        
        order.kind = order.get_kind(order.type_order)
        order.client = Client.select_from_db(client_id)

            
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
    # def __init__(self, seq='') -> None:
    #     super().__init__(seq)

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
    a = Type(name='ada', kind='оф')
    print(a.kind)
        
