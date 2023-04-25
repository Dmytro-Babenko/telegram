from aiogram import Dispatcher, types

from tgbot.filters.admin_filters import IsAdmin

async def start_admin_panel(message: types.Message):
    await message.answer('Адмін')

def hendler_registration(dp: Dispatcher):
    dp.register_message_handler(start_admin_panel, IsAdmin(), commands='admin')
    pass
