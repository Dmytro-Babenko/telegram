from aiogram import Dispatcher, types,filters
from aiogram.dispatcher import FSMContext

from tgbot.database.models import OrderType, University, Subject, DBWorker
from tgbot.filters.admin_filters import IsAdmin
from tgbot.FSMStates.admin import FSMAdding
from tgbot.keyboards.inline_kb import make_choose_kb, make_kind_kb, yes_no_kb
from tgbot.keyboards.reply_kb import make_admin_kb
import tgbot.utils.callback_data as cb_d 
import tgbot.utils.helpers_for_hendlers as hfh

CATEGORIES = {
    'Предмет': Subject,
    'Університет': University,
    'Тип': OrderType
}

async def cancel_adding(update: types.Message|types.CallbackQuery, state: FSMContext):
    await state.finish()
    message = update.message if update.message else update
    await message.answer('Додавання запису скасовано', reply_markup=make_admin_kb())

async def start_admin_panel(message: types.Message):
    admin_kb = make_admin_kb()
    await message.answer('Доступ надано! Користайтеся меню', reply_markup=admin_kb)

async def add(message: types.Message, state: FSMContext):
    await FSMAdding.category.set()
    await ask_to_choose_category(message)
    async with state.proxy() as data:
        data['hendlers_dct'] = STATE_GR_AND_BACK_HENDLERS

async def ask_to_choose_category(message: types.Message, *args):
    categories_kb = make_choose_kb(CATEGORIES, cb_d.categories_cb_data)
    await message.answer('Оберіть тип', reply_markup=categories_kb)

async def choose_category(cb: types.CallbackQuery, state: FSMContext, callback_data):
    category = callback_data['choice']
    print(type(category))
    async with state.proxy() as data:
        data['category'] = category
    await FSMAdding.next()
    await ask_to_write_name(cb.message)

async def ask_to_write_name(message: types.Message, *args):
    await message.answer('Напишіть назву')

async def set_name(message: types.Message, state: FSMContext):
    name = message.text
    async with state.proxy() as data:
        data['name'] = name
        category = data['category']
        if category == 'Тип':
            await FSMAdding.next()
            await ask_to_choose_kind(message)
        else:
            field = create_obj(**data)
            data['obj'] = field
            await FSMAdding.confirmation.set()
            await ask_confirmation(message, field)

async def ask_to_choose_kind(message: types.Message, *args):
        kind_kb = make_kind_kb()
        await message.answer('Оберіть тип', reply_markup=kind_kb)


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
    field: University|Subject|OrderType = class_(name, kind)
    return field

async def ask_confirmation(message: types.Message, __obj):
    text = __obj.show_info()
    await message.answer(text)
    kb = yes_no_kb()
    await message.answer('Підтверджуєте інформацію?', reply_markup=kb)
    
@hfh.errors_interceptor
async def add_to_db(message: types.Message, state: FSMContext, db_worker: DBWorker,*args, **kwargs):
    data = await state.get_data()
    field: University|Subject|OrderType  = data['obj']
    db_worker.insert(field)
    await state.finish()
    await message.answer('Готово')

HENDLERS = (
    ask_to_choose_category, 
    ask_to_write_name, ask_to_choose_kind
    )

STATE_GR_AND_BACK_HENDLERS = hfh.state_gr_and_dct_for_return(FSMAdding, HENDLERS)

def hendler_registration(dp: Dispatcher):
    dp.register_message_handler(start_admin_panel, IsAdmin(), commands='admin')
    dp.register_message_handler(add, IsAdmin(), filters.Text('Додати'))
    dp.register_callback_query_handler(choose_category, cb_d.categories_cb_data.filter(), state=FSMAdding.category)
    dp.register_message_handler(set_name, state=FSMAdding.name)
    dp.register_callback_query_handler(set_kind, cb_d.kind_cb_data.filter(), state=FSMAdding.kind)
    dp.register_callback_query_handler(add_to_db, cb_d.yes_cb_data.filter(), state=FSMAdding.confirmation)
    dp.register_callback_query_handler(cancel_adding, cb_d.no_cb_data.filter(), state=FSMAdding.confirmation)

    dp.register_message_handler(start_admin_panel, IsAdmin())
    pass
