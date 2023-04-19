from collections import UserList, UserString, defaultdict
import sqlite3

from aiogram import types, Bot
from aiogram.types.document import Document

from tgbot.texts.texts import PHOTO_EXTENSION
from tgbot.database.data import DB_FILE

class AbstractModel:
    def __init__(self) -> None:
        pass

    def insert_to_db(self):
        pass

    def select_from_db(self):
        pass 

class Client(AbstractModel):
    def __init__(self, telegram_id, first_name, last_name, username, phone=None) -> None:
        self.telegram_id = telegram_id
        self.first_name = first_name
        self.last_name = last_name
        self.user_name = username
        self.phone = phone
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
    def get_all_ids():
        with sqlite3.connect(DB_FILE) as con:
            con.row_factory = lambda cursor, row: row[0]
            cur = con.cursor()
            sql = 'SELECT telegram_id FROM clients'
            return cur.execute(sql).fetchall()

class Order(AbstractModel):
    def __init__(self, client_id, type_order, subject, datetime, t_or_v, 
                 kind_order ,university=None, order_id=None, task_files=None, 
                 solutions=None, **kwargs) -> None:
        self.order_id = order_id
        self.client_id = client_id
        self.type_order = type_order
        self.subject = subject
        self.datetime = datetime
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

            type_id = select_id('types', self.type_order)
            subject_id = select_id('subjects', self.subject)
            univ_id = select_id('universities', self.university)
            print(self.subject, subject_id)
            print(self.university, univ_id)

            insert_order = """INSERT INTO orders (client_id, type_id, subject_id, order_date, univ_id, theme_or_variant)
                            VALUES (?, ?, ?, ?, ?, ?) """
            values = (self.client_id, type_id, subject_id, self.datetime, univ_id, self.t_or_v)
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

class TextGroup(UserString):
    def __init__(self, seq='') -> None:
        super().__init__(seq)

    async def sending(self, bot:Bot, chat_id):
        await bot.send_message(chat_id, self.data)

    def checking_size(self, new_element):
        return len(new_element) + len(self) <= 4096 - 2
    
    def insert_to_db(self, order_id, file_number, file_group, cur:sqlite3.Cursor=None):
        sql = """INSERT into texts (text_info, pos, file_group, order_id)
                VALUES (?, ?, ?, ?)"""
        values = (self.data, file_number, file_group, order_id)

        if cur:
            cur.execute(sql, values)
            return None
        
        with sqlite3.connect(DB_FILE) as con:
            cur = con.cursor()
            cur.execute(sql, values)

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
            return None
        
        with sqlite3.connect(DB_FILE) as con:
            cur = con.cursor()
            cur.execute(sql, values)

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
        
        with sqlite3.connect(DB_FILE) as con:
            cur = con.cursor()
            cur.execute(sql, values)

class TextElement(FileElement, UserString):

    @file_group_checking(TextGroup)
    def adding(self, lst: list):
        lst[-1].data += f'\n\n{self}'

    def insert_to_db(self, order_id, file_number, file_group, cur:sqlite3.Cursor=None):
        sql = """INSERT into texts (text_info, pos, file_group, order_id)
                VALUES (?, ?, ?, ?)"""
        values = (self.data, file_number, file_group, order_id)

        if cur:
            cur.execute(sql, values)
            return None
        
        with sqlite3.connect(DB_FILE) as con:
            cur = con.cursor()
            cur.execute(sql, values)
    
class Files(UserList):

    def iter_all(self):
        for media_group in self:
            if isinstance(media_group, TextGroup):
                yield media_group
            else:
                for media in media_group:
                    yield media

    def add_element(self, element:DocElement|PhotoElement|TextElement):
        element.adding(self)

    async def send_files(self, bot:Bot, chat_id):
        for group in self:
            group: DocGroup|PhotoGroup|TextGroup
            await group.sending(bot, chat_id)

    async def answer_files(self, message: types.Message):
        await self.send_files(message.bot, message.chat.id)

    def insert_to_db(self, order_id, cur, file_group):
        start_file_pos = 1
        for group in self:
            group: PhotoGroup|DocGroup|TextGroup
            group.insert_elements_to_db(order_id, i, file_group, cur)
        start_file_pos += len()

class Solutions(defaultdict):

    def insert_to_db(self, order_id, cur):
        for task_num, files in self.items():
            files: Files
            print(files)
            files.insert_to_db(order_id, cur, task_num)

        