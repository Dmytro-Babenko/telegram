from aiogram.types.inline_keyboard import InlineKeyboardButton, InlineKeyboardMarkup

from tgbot.database.models import OrderType, University, Subject, DBWorker
from tgbot.utils import callback_data as cb_d


BUTTONS = {
    'type_order': (['Модуль', 'Екзамен', 'Залік'], cb_d.type_order_cb_data),
    'subject': (['Математика', 'Статистика'], cb_d.subject_cb_data),
    'categories': (['Предмет', 'Університет', 'Тип'], cb_d.categories_cb_data) 
}

def make_choose_kb(names, cb_data, row_width=2):
    buttons = [InlineKeyboardButton(text=name, callback_data=cb_data.new(name)) for name in names]
    kb = InlineKeyboardMarkup(row_width=row_width)
    kb.add(*buttons)
    return kb

def make_kind_kb():
    buttons = [InlineKeyboardButton(text=kind, callback_data=cb_d.kind_cb_data.new(kind[:2]))
               for kind in ('офлайн', 'онлайн')]
    kb = InlineKeyboardMarkup()
    kb.add(*buttons)
    return kb

async def make_inline_search_kb():
    search_button = InlineKeyboardButton('Пошук', switch_inline_query_current_chat='')
    kb = InlineKeyboardMarkup(inline_keyboard=[[search_button]])
    return kb

def yes_no_kb():
    return InlineKeyboardMarkup(2, [[InlineKeyboardButton('Так', callback_data=cb_d.yes_cb_data.new('Yes')),
                                     InlineKeyboardButton('Ні', callback_data=cb_d.no_cb_data.new('No'))]])