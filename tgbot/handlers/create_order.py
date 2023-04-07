from collections import defaultdict
from datetime import date, datetime
from functools import reduce

from aiogram import Dispatcher, types
from aiogram.dispatcher import filters, FSMContext
from aiogram.types import InlineQueryResultArticle, InputTextMessageContent, InputMediaPhoto, InputMediaDocument, MediaGroup

from tgbot.database import models
from tgbot.filters.create_order_filters import ListStateFilter
from tgbot.keyboards import reply_kb, inline_kb
from tgbot.keyboards.tg_calendar import TgCalendar, calendar_callback
from tgbot.texts import texts
from tgbot.FSMStates.client_st import FSMCreateOrder
from tgbot.utils.callback_data import subject_cb_data, type_order_cb_data
from tgbot.utils.helpers_for_hendlers import get_file_id_and_ext, delete_state_value

async def back(message: types.Message, state: FSMContext):

    HENDLERS = (
        cancel_order, start_creating, ask_to_choose_sb, 
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

async def start_creating(message:types.Message, *args):
    await FSMCreateOrder.type_order.set()
    inl_kb = await inline_kb.make_choose_kb('type_order')
    create_kb = reply_kb.make_create_order_kb()
    await message.answer('Ви в меню створення замовлень, користуйтесь підсказками', reply_markup=create_kb)
    await message.answer('Оберіть тип роботи будь ласка', reply_markup=inl_kb)

async def ask_to_choose_sb(message:types.Message, *args):
    inl_kb = await inline_kb.make_choose_kb('subject')
    await message.answer('Оберіть предмет', reply_markup=inl_kb)

async def choose_order_type(cq: types.CallbackQuery, state: FSMContext, callback_data: dict):
    message = cq.message
    await message.answer('Тип обрано')
    async with state.proxy() as data:
        data['type_order'] = callback_data['choice']
    await FSMCreateOrder.next()
    await ask_to_choose_sb(message)

async def choose_order_sb(cq: types.CallbackQuery, state: FSMContext, callback_data: dict):
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
    order_date: date= await TgCalendar().selection(cq, callback_data)
    if order_date:
        async with state.proxy() as data:
            data['date'] = order_date
        await FSMCreateOrder.next()
        await cq.message.answer(f'Ви обрали дату {order_date.strftime("%d.%m.%y")}')
        await ask_to_choose_time(cq.message)

async def ask_to_choose_time(message:types.Message, *args):
    await message.answer('Напишіть час')

async def choose_time(message:types.Message, state:FSMContext):
    order_time = datetime.strptime(message.text, '%H:%M').time()
    async with state.proxy() as data:
        data['time'] = order_time
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
        await ask_to_choose_theeme_var(message)
    else:
        await message.answer('Скористайтесь кнопкою пошук')

async def set_uni_variants(query:types.InlineQuery, variants:list):

    text = query.query or ''
    text = text.lower()

    items = [InlineQueryResultArticle(
        input_message_content=InputTextMessageContent(element),
        id=i,
        title=element
    ) for i, element in enumerate(variants) if text in element.lower()]

    if not items:
        items = [InlineQueryResultArticle(
            input_message_content=InputTextMessageContent(text),
            id = 0,
            title=text
        )]

    await query.answer(results=items[:49], cache_time=1, is_personal=True)

async def ask_to_choose_theeme_var(message:types.Message, *args):
    await message.answer('Напишіть тему')

async def choose_theeme_or_variant(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['t_or_v'] = message.text
    await FSMCreateOrder.next()
    await ask_to_send_files(message, state)

async def ask_to_send_files(message:types.Message, state: FSMContext):
    await message.answer('Відправте файли', reply_markup=reply_kb.make_create_order_kb(confirm=True, cancel_files=True))
    async with state.proxy() as data:
        data['files'] = models.Files()

async def get_files(message: types.Message, state: FSMContext):
    if message.photo:
        file_id = message.photo[-1].file_id
        file = models.UserPhoto(file_id)
    else:
        id_and_ext = get_file_id_and_ext(message)
        file = models.UserDoc(*id_and_ext)
    async with state.proxy() as data:
        if data.get('solutions') != None:
            file_sub_group = data.get('task_num', '')
            data['solutions'][file_sub_group].add_file(file)
        else:
            data['files'].add_file(file)

async def finish_sending_task(message: types.Message, state: FSMContext):
    # bot = message.bot
    # async with state.proxy() as data:
    #     for i, (id, stem) in enumerate(data['files'], 1):
    #         file_name = f'{data["t_or_v"]}{i}{stem}'
    #         await bot.download_file_by_id(id, file_name)

    await FSMCreateOrder.next()
    await ask_to_send_solution(message, state)

async def ask_to_send_solution(message: types.Message, state: FSMContext):
    await message.answer('Надішліть будь ласка рішення')
    async with state.proxy() as data:
        data['solutions'] = defaultdict(models.Files)
        data['task_num'] = ''

async def set_task_num(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['task_num'] = message.text

async def cancel_task_sending(message: types.Message, state: FSMContext):
    await delete_state_value(state)
    async with state.proxy() as data:    
        wait_solution = True if data.get('files') != None else False
    if wait_solution:
        await ask_to_send_solution(message, state)
    else:
        await ask_to_send_files(message, state)

async def files_sending(message: types.Message, files_list:list[tuple]):
    media_group = MediaGroup()
    previous_ext = None
    for i, (id_, ext) in enumerate(files_list):
        if ext == '.jpg':
            file_inp_obj = InputMediaPhoto(media=id_)
        else:
            file_inp_obj = InputMediaDocument(media=id_)

        if i > 0 and ((ext == '.jpg') ^ (previous_ext == '.jpg')):
            await message.answer_media_group(media_group)
            media_group.media = []

        media_group.attach(file_inp_obj)
        previous_ext = ext
    await message.answer_media_group(media_group)
    
async def finish_order_creation(message: types.Message, state: FSMContext):
    data = await state.get_data()
    order_description = '\n'.join((f'{x}: {y}' for x, y in data.items()))
    task_files:models.Files = data['files']
    solution_files:defaultdict = data['solutions']
    await message.answer(order_description)
    # print(task_files.media_groups)
    for media_group in task_files.media_groups:
        await message.answer_media_group(media_group)

    for num, files in solution_files.items():
        await message.answer(num)
        for media_group in files.media_groups:
            await message.answer_media_group(media_group)
    
    # await message.answer_media_group(task_files.media_groups)
    # for num, files in solution_files.items():
    #     await message.answer(num)
    #     await files_sending(message, files)

async def no_command(update: types.Message|types.CallbackQuery):
    await update.answer('Неправильна команда, користуйтеся підсказками бота')

def handlers_registration(dp: Dispatcher):
    dp.register_message_handler(start_creating, filters.Text('Зробити замовлення'))
    dp.register_message_handler(cancel_order, filters.Text('Скасувати замовлення'), state='*')
    dp.register_message_handler(back, filters.Text('Назад'), state='*')

    dp.register_callback_query_handler(choose_order_type, type_order_cb_data.filter(), state=FSMCreateOrder.type_order)
    dp.register_callback_query_handler(choose_order_sb, subject_cb_data.filter(), state=FSMCreateOrder.subject)
    dp.register_callback_query_handler(choose_date, calendar_callback.filter(), state=FSMCreateOrder.date)
    dp.register_message_handler(choose_time, filters.Regexp(texts.TIME_REGEX), state=FSMCreateOrder.time)
    dp.register_message_handler(wrong_time, state=FSMCreateOrder.time)
    dp.register_inline_handler(set_uni_variants, ListStateFilter(FSMCreateOrder.university), state=FSMCreateOrder.university)
    dp.register_message_handler(choose_uni, state=FSMCreateOrder.university)
    dp.register_message_handler(choose_theeme_or_variant, state=FSMCreateOrder.t_or_v)

    dp.register_message_handler(finish_sending_task, filters.Text('Підтвердити'), state=FSMCreateOrder.files)
    dp.register_message_handler(get_files, state=[FSMCreateOrder.files, FSMCreateOrder.solutions], content_types=['document', 'photo'])
    dp.register_message_handler(cancel_task_sending, filters.Text('Скасувати відправку файлів'), state=[FSMCreateOrder.files, FSMCreateOrder.solutions])
    dp.register_message_handler(finish_order_creation, filters.Text('Підтвердити'), state=FSMCreateOrder.solutions)
    dp.register_message_handler(set_task_num, state=FSMCreateOrder.solutions, regexp='\w{1,3}')

    dp.register_callback_query_handler(no_command, state='*')
    dp.register_message_handler(no_command, state='*')







