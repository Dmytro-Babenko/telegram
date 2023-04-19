import re

from aiogram import types
from aiogram.dispatcher import FSMContext

from tgbot.database import models

def need_admin():
    def decorator(func):
        setattr(func, 'need_admins', True)
        return func
    return decorator

def get_file_id_and_ext(message: types.Message) -> tuple[str, str]:
    file_id = message.document.file_id
    file_stem = f'.{message.document.file_name.split(".")[-1]}'
    return file_id, file_stem

def define_file(message: types.Message):
    if message.photo:
        file_id = message.photo[-1].file_id
        file = models.PhotoElement(media=file_id)
    else:
        file_id, ext = get_file_id_and_ext(message)
        file = models.DocElement(media=file_id, extension=ext)
    return file 

def define_text_material(message: types.Message, need_task_num = False):
    text = message.text
    file = models.TextElement(text)
    if need_task_num:
        print(text)
        task_num_match = re.search(r'^\d{1,3}\b', text)
        print(task_num_match)
        task_num = task_num_match.group() if task_num_match else None
        return file, task_num
    return file

def put_sollution_to_data(data, file, task_num=None):
    if task_num:
        data['task_num'] = task_num
    file_sub_group = data.get('task_num', '')
    files:models.Files = data['solutions'][file_sub_group]
    files.add_element(file)

async def delete_state_value(state: FSMContext):
        state_name = await state.get_state()
        if state_name:
            state_short_name = state_name.split(':')[1]
            async with state.proxy() as data:
                if data.get(state_short_name) != None:
                    data.pop(state_short_name)


            
