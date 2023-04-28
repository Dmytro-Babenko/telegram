from aiogram import Dispatcher, types,filters
from aiogram.dispatcher import FSMContext

from tgbot.database.models import OrderType, University, Subject
from tgbot.filters.admin_filters import IsAdmin
from tgbot.FSMStates.admin import FSMAdding, FSMAddingType
from tgbot.keyboards.inline_kb import make_choose_kb, make_kind_kb
from tgbot.keyboards.reply_kb import make_admin_kb
from tgbot.utils.callback_data import categories_cb_data, kind_cb_data

CATEGORIES = {
    'Предмет': Subject,
    'Університет': University,
    'Тип': OrderType
}

async def start_admin_panel(message: types.Message):
    admin_kb = make_admin_kb()
    await message.answer('Доступ надано! Користайтеся меню', reply_markup=admin_kb)

async def add(message: types.Message):
    await FSMAdding.category.set()
    categories_kb = await make_choose_kb('categories')
    await message.answer('Оберіть тип', reply_markup=categories_kb)

async def choose_category(cb: types.CallbackQuery, state: FSMContext, callback_data):
    category = callback_data['choice']
    print(type(category))
    async with state.proxy() as data:
        data['category'] = category
    await FSMAdding.next()
    await cb.message.answer('Напишіть назву')

async def set_name(message: types.Message, state: FSMContext):
    name = message.text
    async with state.proxy() as data:
        data['name'] = name
        category = data['category']
        if category == 'Тип':
            await FSMAdding.next()
            kind_kb = make_kind_kb()
            await message.answer('Оберіть тип', reply_markup=kind_kb)
        else:
            field = create_obj(**data)
            data['obj'] = field
            await FSMAdding.confirmation.set()
            await ask_confirmation(message, field)
            
async def set_kind(cb: types.CallbackQuery, state: FSMContext, callback_data):
    kind = callback_data['choice']
    message = cb.message
    async with state.proxy() as data:
        data['kind'] = kind
        a = {**data}
        field = create_obj(**data)
        data['obj'] = field
    await FSMAdding.next()
    await ask_confirmation(message, field)

def create_obj(category, name, kind=None, **args):
    class_ = CATEGORIES.get(category)
    print(kind)
    field: University|Subject|OrderType = class_(name, kind)
    return field

async def ask_confirmation(message: types.Message, __obj):
    text = __obj.show_info()
    await message.answer(text)
    await message.answer('Підтверджуєте інформацію?')
    
async def add_to_db(message: types.Message, state: FSMContext):
    data = await state.get_data()
    field: University|Subject|OrderType  = data['obj']
    field.insert_to_db()
    await state.finish()
    await message.answer('Готово')

def hendler_registration(dp: Dispatcher):
    dp.register_message_handler(start_admin_panel, IsAdmin(), commands='admin')
    dp.register_message_handler(add, IsAdmin(), filters.Text('Додати'))
    dp.register_callback_query_handler(choose_category, categories_cb_data.filter(), state=FSMAdding.category)
    dp.register_message_handler(set_name, state=FSMAdding.name)
    dp.register_callback_query_handler(set_kind, kind_cb_data.filter(), state=FSMAdding.kind)
    dp.register_message_handler(add_to_db, filters.Text('Так'), state=FSMAdding.confirmation)
    pass
