from aiogram import Dispatcher, types,filters
from aiogram.dispatcher import FSMContext

from tgbot.database.models import OrderType, University, Subject
from tgbot.filters.admin_filters import IsAdmin
from tgbot.FSMStates.admin import FSMAdding, FSMAddingType
from tgbot.keyboards.inline_kb import make_choose_kb, make_kind_kb, yes_no_kb
from tgbot.keyboards.reply_kb import make_admin_kb
import tgbot.utils.callback_data as cb_d 
import tgbot.utils.helpers_for_hendlers as hfh

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
    kb = yes_no_kb()
    await message.answer('Підтверджуєте інформацію?', reply_markup=kb)
    
@hfh.errors_interceptor
async def add_to_db(message: types.Message, state: FSMContext, *args, **kwargs):
    data = await state.get_data()
    field: University|Subject|OrderType  = data['obj']
    field.insert_to_db()
    await state.finish()
    await message.answer('Готово')

async def cancel_adding(message: types.Message, state: FSMContext):
    pass

def hendler_registration(dp: Dispatcher):
    dp.register_message_handler(start_admin_panel, IsAdmin(), commands='admin')
    dp.register_message_handler(add, IsAdmin(), filters.Text('Додати'))
    dp.register_callback_query_handler(choose_category, cb_d.categories_cb_data.filter(), state=FSMAdding.category)
    dp.register_message_handler(set_name, state=FSMAdding.name)
    dp.register_callback_query_handler(set_kind, cb_d.kind_cb_data.filter(), state=FSMAdding.kind)
    dp.register_callback_query_handler(add_to_db, cb_d.yes_cb_data.filter(), state=FSMAdding.confirmation)
    dp.register_callback_query_handler(cancel_adding, cb_d.no_cb_data.filter(), state=FSMAdding.confirmation)
    pass
