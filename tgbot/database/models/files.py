from abc import ABC, abstractmethod

from collections import UserList, defaultdict, UserString
from collections.abc import Iterable
import sqlite3

from aiogram import types, Bot

PHOTO_EXTENSION='.jpg'

def file_group_checking(group_type):
    def decorator(func):
        def inner(self, lst: list, *args):
            if not (lst and isinstance(lst[-1], group_type) and lst[-1].checking_size(self)):
                lst.append(group_type())
            func(self, lst, *args)
        return inner
    return decorator

class FilesGroup(ABC):

    @abstractmethod
    async def sending(self, bot, chat_id):
        pass

    @abstractmethod
    def checking_size(self):
        pass

class CustomMediaGroup(UserList, FilesGroup):
    async def sending(self, bot:Bot, chat_id):
        await bot.send_media_group(chat_id, self.data)

    def checking_size(self):
        return len(self) < 10
    
    def __add__(self, other: Iterable):
        return self.extend(other)

class DocGroup(CustomMediaGroup):
    pass

class PhotoGroup(CustomMediaGroup):
    pass

class TextGroup(UserList, FilesGroup):

    __limit = 4090
    async def sending(self, bot:Bot, chat_id):
        for text in self:
            await bot.send_message(chat_id, text.data)

    def checking_size(self):
        return True
    
    def __add__(self, other: Iterable):
        # print(other)
        if self[-1] and len(self[-1]) + len(other[-1]) < self.__limit:
            self[-1] += f'\n\n{other[-1]}'
        else:
            self.extend(other)

class FileElement:
    _group = None

    def adding(self, lst: list):
        lst[-1].append(self)

    def make_group(self):
        return self._group([self])

    def insert_to_db(self):
        pass

class PhotoElement(types.InputMediaPhoto, FileElement):

    _group = PhotoGroup

    def __init__(self, *args, extension=PHOTO_EXTENSION, **kwargs):
        super().__init__(*args, **kwargs)
        self.extension = extension

    @file_group_checking(PhotoGroup)
    def adding(self, lst: list):
        super().adding(lst)

    def insert_to_db(self, order_id, file_number, file_group, cur):
        sql = """INSERT into photos (telegram_id, pos, file_group, order_id)
                VALUES (?, ?, ?, ?)"""
        values = (self.media, file_number, file_group, order_id)
        cur.execute(sql, values)
        
class DocElement(types.InputMediaDocument, FileElement):

    _group = DocGroup

    def __init__(self, extension, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.extension = extension

    @file_group_checking(DocGroup)
    def adding(self, lst: list[list]):
        super().adding(lst)

    def insert_to_db(self, order_id, file_number, file_group, cur):
        sql = """INSERT into documents (telegram_id, pos, file_group, order_id)
                VALUES (?, ?, ?, ?)"""
        values = (self.media, file_number, file_group, order_id)
        cur.execute(sql, values)
        return None

class TextElement(FileElement, UserString):

    _group =TextGroup

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

    @property
    def previous_group(self):
        try:
            prev : DocGroup|TextGroup|PhotoGroup = self[-1]
            return prev
        except IndexError:
            return None

    def is_prev_open(self):
        if self.previous_group:
            return self.previous_group.checking_size()
        return False

    def iter_all(self):
        for media_group in self:
            for media in media_group:
                yield media

    def add_element(self, element:DocElement|PhotoElement|TextElement):
        group = element.make_group()
        prev = self.previous_group
        print(type(prev), type(group))
        if type(group) == type(prev) and self.is_prev_open():
            self.previous_group + group
        else:
            self.append(group)

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
    a = Files()
    a.add_element(DocElement(media=213123123, extension='asd'))
    a.add_element(DocElement(media=111111111, extension='asd'))
    print(a)