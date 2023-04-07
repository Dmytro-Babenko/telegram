from collections import UserDict, defaultdict, UserList

from aiogram import types
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

class UserFile():
    def __init__(self, file_id) -> None:
        self.id = file_id
        self.extension = None
        pass

    def make_input_media(self):
        pass

class UserPhoto(UserFile):
    def __init__(self, file_id, extension=PHOTO_EXTENSION) -> None:
        super().__init__(file_id)
        self.extension = extension

    def make_input_media(self):
        return types.InputMediaPhoto(media=self.id)

class UserDoc(UserFile):
    def __init__(self, file_id, extension:str) -> None:
        super().__init__(file_id)
        self.extension = extension

    def make_input_media(self):
        return types.InputMediaDocument(media=self.id)

class Files(UserList):
    def __init__(self, liste=None):
        super().__init__(liste)
        self.media_groups = []

    def form_media_groups(self) -> None:

        if not self:
            return None
        
        media_group = types.MediaGroup()
        previous_file = self[0]
        for file in self:
            file:UserDoc|UserPhoto
            file_inp_obj = file.make_input_media()

            if not isinstance(file, type(previous_file)):
                self.media_groups.append(media_group)
                media_group.media = []

            media_group.attach(file_inp_obj)
            previous_file = file
        self.media_groups.append(media_group)
        pass

    def add_file(self, file:UserPhoto|UserDoc):
        file_inp_obj = file.make_input_media()
        if not self or type(self[-1]) != type(file):
            media_group = types.MediaGroup()
            media_group.attach(file_inp_obj)
            self.media_groups.append(media_group)
        else:
            self.media_groups[-1].attach(file_inp_obj)
        self.append(file)

