from datetime import date, datetime
import re

from aiogram import Dispatcher, types
from aiogram.dispatcher import filters, FSMContext
from aiogram.types import InlineQueryResultArticle, InputTextMessageContent

from tgbot.database import models
from tgbot.filters.create_order_filters import ListStateFilter, IsAdmin
from tgbot.keyboards import reply_kb, inline_kb
from tgbot.keyboards.tg_calendar import TgCalendar, calendar_callback
from tgbot.texts import texts
from tgbot.FSMStates.client_st import FSMCreateOrder
from tgbot.utils.callback_data import subject_cb_data, type_order_cb_data
from tgbot.utils.helpers_for_hendlers import delete_state_value, put_sollution_to_data, define_file, define_text_material

async def back(message: types.Message, state: FSMContext):

    HENDLERS = (
        cancel_order, cancel_order, ask_to_choose_type, ask_to_choose_sb, 
        ask_to_choose_date, ask_to_choose_time, ask_to_choose_uni,
        ask_to_choose_theeme_var, ask_to_send_files, ask_to_send_solution
        )
    
    back_hendlers = {
        state_name:hendler for state_name, hendler 
        in zip(FSMCreateOrder.all_states_names, HENDLERS)
        }
    
    back_hendler = back_hendlers.get(await state.get_state(), cancel_order)
    await delete_state_value(state)
    await FSMCreateOrder.previous()
    await delete_state_value(state)
    print(await state.get_data())
    await back_hendler(message, state)

async def cancel_order(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer('Оформлення замовлення скасовано', reply_markup=reply_kb.make_main_kb())

async def send_create_kb(message: types.Message):
    create_kb = reply_kb.make_create_order_kb()
    await message.answer('Ви в меню створення замовлень, користуйтесь підсказками', reply_markup=create_kb)

async def start_creating(message:types.Message, state: FSMContext):
    await FSMCreateOrder.type_order.set()
    await send_create_kb(message)
    await ask_to_choose_type(message)
    client = models.Loader.load_from_db(message.from_user.id, models.Client)
    async with state.proxy() as data:
        data['client'] = client

async def start_admin_creating(message: types.Message, *args):
    await FSMCreateOrder.client.set()
    await send_create_kb(message)
    await message.answer('Перещліть повідомлення від клієнта')

async def set_client(message: types.Message, state: FSMContext):
    client_id = message.forward_from.id
    if client_id in models.Loader.load_all(models.Client):
        client = models.Loader.load_from_db(client_id, models.Client)
    else:
        first_name = message.forward_from.first_name
        last_name = message.forward_from.last_name
        user_name = message.forward_from.username
        client = models.Client(client_id, first_name, last_name, user_name)
        client.insert_to_db()

    async with state.proxy() as data:
        data['client'] = client
    
    await FSMCreateOrder.next()
    await ask_to_choose_type(message)

async def ask_to_choose_type(message: types.Message, *args):
    inl_kb = await inline_kb.make_choose_kb('type_order')
    await message.answer('Оберіть тип роботи будь ласка', reply_markup=inl_kb)

async def choose_order_type(cq: types.CallbackQuery, state: FSMContext, callback_data: dict):
    message = cq.message
    order_type = callback_data['choice']
    await message.answer('Тип обрано')
    async with state.proxy() as data:
        data['type_order'] = order_type
        # data['kind_order'] = models.Order.get_kind(order_type)
    await FSMCreateOrder.next()
    await ask_to_choose_sb(message)

async def ask_to_choose_sb(message:types.Message, *args):
    inl_kb = await inline_kb.make_choose_kb('subject')
    await message.answer('Оберіть предмет', reply_markup=inl_kb)

async def choose_order_sb(cq: types.CallbackQuery, state: FSMContext, callback_data: dict, raw_state):
    print(raw_state)
    await cq.message.answer('Предмет обрано')
    async with state.proxy() as data:
        data['subject'] = callback_data['choice']
    await FSMCreateOrder.next()
    await ask_to_choose_date(cq.message)

async def ask_to_choose_date(message:types.Message, *args):
    tg_clndr = TgCalendar()
    kb = await tg_clndr.start_calendar()
    await message.answer('оберіть дату', reply_markup=kb)

async def choose_date(cq: types.CallbackQuery, state: FSMContext, callback_data: dict):
    order_date:date = await TgCalendar().selection(cq, callback_data)
    if order_date:
        async with state.proxy() as data:
            data['datetime'] = order_date
        await FSMCreateOrder.next()
        await cq.message.answer(f'Ви обрали дату {order_date.strftime("%d.%m.%y")}')
        await ask_to_choose_time(cq.message)

async def ask_to_choose_time(message:types.Message, *args):
    await message.answer('Напишіть час')

async def choose_time(message:types.Message, state:FSMContext):
    order_time = datetime.strptime(message.text, '%H:%M').time()
    async with state.proxy() as data:
        date = data['datetime']
        data['datetime'] = datetime.combine(date, order_time)
    await FSMCreateOrder.next()
    await message.answer(f'Ви обрали час {message.text}')
    await ask_to_choose_uni(message)

async def wrong_time(message:types.Message):
    await message.answer('Невірний формат, напишість час в фокматі 16:30')

async def ask_to_choose_uni(message:types.Message, *args):
    await message.answer('Оберіть університет', reply_markup=await inline_kb.make_inline_search_kb())

async def choose_uni(message:types.Message, state:FSMContext):
    if message.via_bot:
        async with state.proxy() as data:
            data['university'] = message.text
        await FSMCreateOrder.next()
        await ask_to_choose_theeme_var(message, state)
    else:
        await message.answer('Скористайтесь кнопкою пошук')

async def set_uni_variants(query:types.InlineQuery, variants:list, prev_variants:list):

    def make_items(text, variants):
        items = [
            InlineQueryResultArticle(
                input_message_content=InputTextMessageContent(element),
                id=i, title=element
            ) for i, element in enumerate(variants) if text in element.lower()]
        return items

    text = query.query or ''
    text = text.lower()

    items = make_items(text, prev_variants)
    if not items:
        items = make_items(text, variants)
        if not items:
            items = make_items(text, [text])

    await query.answer(results=items[:49], cache_time=1, is_personal=True)

async def ask_to_choose_theeme_var(message:types.Message, state: FSMContext, *args):
    async with state.proxy() as data:
        order_type = models.Loader.load_by_name(data['type_order'], models.OrderType)
        data['order_type'] = order_type
    kind = order_type.kind
    text = 'Напишіть тему' if kind == 'оф' else 'Напишіть варіант'
    await message.answer(text)

async def choose_theeme_or_variant(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['t_or_v'] = message.text
    await FSMCreateOrder.next()
    await ask_to_send_files(message, state)

async def ask_to_send_files(message:types.Message, state: FSMContext):
    await message.answer('Відправте файли', reply_markup=reply_kb.make_create_order_kb(confirm=True, cancel_files=True))
    async with state.proxy() as data:
        data['task_files'] = models.Files()

async def ask_to_send_solution(message: types.Message, state: FSMContext):
    await message.answer('Надішліть будь ласка рішення')
    async with state.proxy() as data:
        data['solutions'] = models.Solutions(models.Files)
        data['task_num'] = ''

async def get_task_files(message: types.Message, state: FSMContext):
    file = define_file(message)
    async with state.proxy() as data:
        files:models.Files = data['task_files']
        files.add_element(file)

async def get_solution_files(message: types.Message, state: FSMContext):
    file = define_file(message)
    async with state.proxy() as data:
        put_sollution_to_data(data, file)

async def get_text_task(message: types.Message, state: FSMContext):
    file = define_text_material(message)
    async with state.proxy() as data:
        files: models.Files = data['task_files']
        files.add_element(file)

async def get_text_solution(message: types.Message, state: FSMContext):
    file, task_num = define_text_material(message, True)
    async with state.proxy() as data:
        put_sollution_to_data(data, file, task_num=task_num)

async def finish_sending_task(message: types.Message, state: FSMContext):
    # bot = message.bot
    # async with state.proxy() as data:
    #     for i, (id, stem) in enumerate(data['files'], 1):
    #         file_name = f'{data["t_or_v"]}{i}{stem}'
    #         await bot.download_file_by_id(id, file_name)

    await FSMCreateOrder.next()
    await ask_to_send_solution(message, state)

async def set_task_num(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['task_num'] = message.text

async def cancel_task_sending(message: types.Message, state: FSMContext):
    await delete_state_value(state)
    await ask_to_send_files(message, state)

async def cancel_solution_sending(message: types.Message, state: FSMContext):
    await delete_state_value(state)
    await ask_to_send_solution(message, state)
    
async def finish_order_creation(message: types.Message, state: FSMContext):
    data = await state.get_data()
    
    client = data['client']
    type_order = data['order_type']
    university = models.Loader.load_by_name(data['university'], models.University)
    subject = models.Loader.load_by_name(data['subject'], models.Subject)
    task_files: models.Files = data['task_files']
    solution_files: models.Solutions[str:models.Files] = data['solutions']
    t_or_v = data['t_or_v']
    date_time = data['datetime']

    order = models.Order(
        client, type_order, subject, date_time, t_or_v, university, 
        task_files=task_files, solutions=solution_files
        )
    
    order_description = order.form_description()
    await message.answer(order_description)
    await task_files.answer_files(message)
    await solution_files.answer_solutions(message)
    order.insert_to_db()

async def no_command(update: types.Message|types.CallbackQuery, state:FSMContext):
    await update.answer('Неправильна команда, користуйтеся підсказками бота')

async def no_state(message: types.Message):
    main_kb = reply_kb.make_main_kb()
    await message.answer('Скористайтесь меню', reply_markup=main_kb)

def handlers_registration(dp: Dispatcher):

    dp.register_message_handler(cancel_order, filters.Text('Скасувати замовлення'), state='*')
    dp.register_message_handler(back, filters.Text('Назад'), state='*')

    dp.register_message_handler(start_admin_creating, IsAdmin(), filters.Text('Зробити замовлення'))
    dp.register_message_handler(start_creating, filters.Text('Зробити замовлення'))
    dp.register_message_handler(set_client, filters.ForwardedMessageFilter(True), state=FSMCreateOrder.client)

    dp.register_callback_query_handler(choose_order_type, type_order_cb_data.filter(), state=FSMCreateOrder.type_order)
    dp.register_callback_query_handler(choose_order_sb, subject_cb_data.filter(), state=FSMCreateOrder.subject)
    dp.register_callback_query_handler(choose_date, calendar_callback.filter(), state=FSMCreateOrder.date)
    dp.register_message_handler(choose_time, filters.Regexp(texts.TIME_REGEX), state=FSMCreateOrder.time)
    dp.register_message_handler(wrong_time, state=FSMCreateOrder.time)
    dp.register_inline_handler(set_uni_variants, ListStateFilter(dp, FSMCreateOrder.university), state=FSMCreateOrder.university)
    dp.register_message_handler(choose_uni, state=FSMCreateOrder.university)
    dp.register_message_handler(choose_theeme_or_variant, state=FSMCreateOrder.t_or_v)

    dp.register_message_handler(cancel_task_sending, filters.Text('Скасувати відправку файлів'), state=[FSMCreateOrder.task_files])
    dp.register_message_handler(finish_sending_task, filters.Text('Підтвердити'), state=FSMCreateOrder.task_files)
    dp.register_message_handler(get_text_task, state=FSMCreateOrder.task_files, regexp=r'.{20,}')
    dp.register_message_handler(get_task_files, state=FSMCreateOrder.task_files, content_types=['document', 'photo'])
    
    dp.register_message_handler(cancel_solution_sending, filters.Text('Скасувати відправку файлів'), state=[FSMCreateOrder.solutions])
    dp.register_message_handler(finish_order_creation, filters.Text('Підтвердити'), state=FSMCreateOrder.solutions)
    dp.register_message_handler(set_task_num, state=FSMCreateOrder.solutions, regexp=re.compile(r'^\w{1,3}$', re.DOTALL))
    dp.register_message_handler(get_text_solution, state=FSMCreateOrder.solutions, regexp=r'.{20,}') 
    dp.register_message_handler(get_solution_files, state=[FSMCreateOrder.solutions], content_types=['document', 'photo'])

    dp.register_message_handler(no_state, state=None)
    dp.register_callback_query_handler(no_command, state='*')
    dp.register_message_handler(no_command, state='*')




