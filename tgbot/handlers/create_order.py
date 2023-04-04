from datetime import date, datetime
import hashlib

from aiogram import Dispatcher, types
from aiogram.dispatcher import filters, FSMContext
from aiogram.types import InlineQueryResultArticle, InputTextMessageContent
from aiogram.types.reply_keyboard import ReplyKeyboardRemove

from tgbot.database.models import Client
from tgbot.database.data import universities
from tgbot.filters.create_order_filters import ListStateFilter
from tgbot.keyboards import reply_kb, inline_kb
from tgbot.keyboards.tg_calendar import TgCalendar, calendar_callback
from tgbot.texts import texts
from tgbot.FSMStates.client_st import FSMCreateOrder
from tgbot.middlewares.common_mw import AdminsIDs, contacts
from tgbot.utils.callback_data import subject_cb_data, type_order_cb_data

async def back(message: types.Message, state: FSMContext):

    HENDLERS = (
        cancel_order, start_creating, ask_to_choose_sb, 
        ask_to_choose_date, ask_to_choose_time, ask_to_choose_uni)
    back_hendlers = {
        state_name:hendler for state_name, hendler 
        in zip(FSMCreateOrder.all_states_names, HENDLERS)
        }
    
    back_hendler = back_hendlers.get(await state.get_state(), cancel_order)
    await FSMCreateOrder.previous()
    previous_state_name = await state.get_state()
    if previous_state_name:
        async with state.proxy() as data:
            data.pop(previous_state_name.split(':')[1])
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
        await ask_to_send_files(message)
    else:
        await message.answer('Скористайтесь кнопкою пошук')

async def ask_to_send_files(message:types.Message, *args):
    await message.answer('Відправте файли')

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

async def save_files(message: types.Message):
    # finish_message_id = message.message_id
    # chat_id = message.chat.id
    print(message)
    file_id = message.document.file_id
    file_name = message.document.file_name
    bot = message.bot
    await bot.download_file_by_id(file_id=file_id, destination=file_name)
    await message.answer('Done')
    # bot
    # print(type(message.chat.ge))  
    # a = types.Message(message_id=finish_message_id,
    #             # date=datetime.datetime.now(),
    #             chat=types.Chat(id=chat_id, type="private"))
    # print(a.text, message.text)

    #сохранняем на последнем єтапе, скасувати - очищает список, словарь, номер файла(длина словаря)

def handlers_registration(dp: Dispatcher):
    # dp.register_message_handler(save_files, content_types=['document'])
    dp.register_message_handler(start_creating, filters.Text('Зробити замовлення'))
    dp.register_message_handler(cancel_order, filters.Text('Скасувати замовлення'), state='*')
    dp.register_message_handler(back, filters.Text('Назад'), state='*')
    dp.register_callback_query_handler(choose_order_type, type_order_cb_data.filter(), state=FSMCreateOrder.type_order)
    dp.register_callback_query_handler(choose_order_sb, subject_cb_data.filter(), state=FSMCreateOrder.subject)
    dp.register_callback_query_handler(choose_date, calendar_callback.filter(), state=FSMCreateOrder.date)
    dp.register_message_handler(choose_time, filters.Regexp(texts.TIME_REGEX), state=FSMCreateOrder.time)
    dp.register_message_handler(wrong_time, state=FSMCreateOrder.time)
    dp.register_inline_handler(set_uni_variants,  ListStateFilter(FSMCreateOrder.university), state=FSMCreateOrder.university)
    dp.register_message_handler(choose_uni, state=FSMCreateOrder.university)


