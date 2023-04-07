from aiogram import types
from aiogram.dispatcher import FSMContext

def need_admin():
    def decorator(func):
        setattr(func, 'need_admins', True)
        return func
    return decorator

def get_file_id_and_ext(message: types.Message) -> tuple[str, str]:
    file_id = message.document.file_id
    file_stem = f'.{message.document.file_name.split(".")[-1]}'
    return file_id, file_stem

async def delete_state_value(state: FSMContext):
        state_name = await state.get_state()
        if state_name:
            state_short_name = state_name.split(':')[1]
            async with state.proxy() as data:
                if data.get(state_short_name) != None:
                    data.pop(state_short_name)
            
