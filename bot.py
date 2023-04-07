import asyncio
import logging

from aiogram import Dispatcher, Bot, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from tgbot import config
from tgbot.handlers import common, create_order
from tgbot.middlewares.common_mw import RegistrationUsers, AdminsIDs, CallbackQueryAnswer
from tgbot.filters.create_order_filters import ListStateFilter

def register_middlewares(dp: Dispatcher):
    dp.setup_middleware(RegistrationUsers())
    dp.setup_middleware(AdminsIDs())
    dp.setup_middleware(CallbackQueryAnswer())
    pass

def register_filters(dp: Dispatcher):
    dp.bind_filter(ListStateFilter)
    pass

def register_handlers(dp: Dispatcher):
    common.hendlers_registration(dp)
    create_order.handlers_registration(dp)
    pass

def main():
    cg = config.load_config('.env')
    bot = Bot(cg.tg_bot.token)
    bot['config'] = cg
    dp = Dispatcher(bot ,storage=MemoryStorage())
    register_middlewares(dp)
    register_filters(dp)
    register_handlers(dp)
    return dp

if __name__ == '__main__':
    dp = main()
    executor.start_polling(dp, skip_updates=True)
# использовать мидлварь чтобы передавать списки поиска в инлайн либо по стейту


# document1 ='document1'
# photo1 = 'photo1'
# document2 = 'document2'

# file_list = []

# file_list.append(document1)
# file_list.append(photo1)
# file_list.append(document2)

# file_list = ['document1', 'photo1', 'document2']
# file_structure = {'docs': ['document1', 'document2'],
#                   'photo': ['photo1']}

# print(file_list)