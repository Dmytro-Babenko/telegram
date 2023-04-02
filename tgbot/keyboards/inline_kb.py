from aiogram.types.inline_keyboard import InlineKeyboardButton, InlineKeyboardMarkup

from tgbot.utils.callback_data import subject_cb_data, type_order_cb_data

BUTTONS = {
    'type_order': (['Модуль', 'Екзамен', 'Залік'], type_order_cb_data),
    'subject': (['Матемвтика', 'Статистика'], subject_cb_data)
}

async def make_choose_kb(state: str):
    lst, cb_data = BUTTONS.get(state, ([], None))
    buttons = [InlineKeyboardButton(text=name, callback_data=cb_data.new(name)) for name in lst]
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(*buttons)
    return kb


async def make_inline_search_kb():
    search_button = InlineKeyboardButton('Пошук', switch_inline_query_current_chat='')
    kb = InlineKeyboardMarkup(inline_keyboard=[[search_button]])
    return kb