from collections import UserDict, defaultdict, UserList, UserString

from aiogram import types, Bot
from aiogram.types.document import Document

from tgbot.texts.texts import PHOTO_EXTENSION

class Client:
    def __init__(self, id, first_name, last_name, username, phone) -> None:
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.user_name = username
        self.phone = phone
        pass

class CustomMediaGroup(UserList):
    async def sending(self, bot:Bot, chat_id):
        await bot.send_media_group(chat_id, self.data)

class DocGroup(CustomMediaGroup):
    pass

class PhotoGroup(CustomMediaGroup):
    pass

class TextGroup(UserList):
    async def sending(self, bot:Bot, chat_id):
        text = '\n\n'.join(str(text) for text in self)
        await bot.send_message(chat_id, text)

class FileElement:
    def adding(self, lst: list):
        lst[-1].append(self)

    def sending(self, bot:Bot, chat_id):
        bot.send_media_group(chat_id, self)

def file_group_checking(group_type):
    def decorator(func):
        def inner(self, lst: list, *args):
            if not (lst and isinstance(lst[-1], group_type) and len(lst[-1]<10)):
                lst.append(group_type())
            func(self, lst, *args)
        return inner
    return decorator

class PhotoElement(types.InputMediaPhoto, FileElement):
    def __init__(self, *args, extension=PHOTO_EXTENSION, **kwargs):
        super().__init__(*args, **kwargs)
        self.extension = extension

    def adding(self, lst: list):
        if not (lst and isinstance(lst[-1], PhotoGroup) and len(lst[-1]<10)):
            lst.append(PhotoGroup())
        super().adding(lst)

class DocElement(types.InputMediaDocument, FileElement):
    def __init__(self, extension, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.extension = extension

    def adding(self, lst: list[list]):
        if not lst or not isinstance(lst[-1], DocGroup):
            lst.append(DocGroup())
        super().adding(lst)

class TextElement(UserString):
    def adding(self, lst: list):
        if not lst or not isinstance(lst[-1], TextGroup):
            lst.append(TextGroup())
        lst[-1].append(self)

class Files(UserList):

    # def add_file(self, __file:PhotoElement|DocElement):
    #     type_file = type(__file)
    #     if not self or not isinstance(self[-1][-1], type_file):
    #         if isinstance(type_file, str):
    #             self.append(TextGroup())
    #         else:
    #             self.append(CustomMediaGroup())
    #     self[-1].append(__file)

    def iter_all(self):
        for media_group in self:
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

    
        