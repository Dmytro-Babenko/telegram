from aiogram import Dispatcher, types
from aiogram.dispatcher import filters, FSMContext
from aiogram.types.reply_keyboard import ReplyKeyboardRemove

from tgbot.database.models import Client
from tgbot.keyboards import reply_kb
from tgbot.texts import texts
from tgbot.filters.create_order_filters import ListStateFilter
from tgbot.FSMStates.client_st import FSMRegistration
from tgbot.middlewares.common_mw import AdminsIDs, contacts
from tgbot.utils.decor_for_hendlers import need_admin

def get_full_name(first_name, last_name):
    return f'{first_name} {last_name}' if last_name else first_name

async def known_start(message: types.Message):
    await message.answer('Hello')
    # id_con = message.from_user.id
    # contact = contacts[id_con]
    # await message.answer(f'Hello {contact.firstname} {contact.lastname}')

async def registration(message:types.Message, state:FSMContext):
    if await filters.IsSenderContact(True).check(message):
        client = Client(
            message.from_user.id,
            message.from_user.first_name,
            message.from_user.last_name,
            message.from_user.username,
            message.contact.phone_number
        )
        contacts[client.id] = client
        name = get_full_name(client.first_name, client.last_name)
        await message.answer(f'{name}, Вас зареєстровано успішно', reply_markup=reply_kb.make_main_kb())
        await state.finish()
    else:
        await message.answer('Вибачте, це не ваш контакт')

async def no_command(message: types.Message):
    await message.answer('There are no command')

@need_admin()
async def send_link_to_admin(message: types.Message, admin):
    await message.answer(
        f'Щоб написати адміну перейдіть за посиланням:\n{texts.TG_LINK}{admin}'
        )
    
def hendlers_registration(dp: Dispatcher):
    dp.register_message_handler(known_start, commands='start')
    dp.register_message_handler(registration,content_types='contact', state=FSMRegistration.contact)
    dp.register_message_handler(send_link_to_admin, filters.Text(equals='Написати адміну'))
    # dp.register_message_handler(no_command)
    

