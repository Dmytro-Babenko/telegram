import asyncio
import logging

from aiogram import Dispatcher, Bot, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from tgbot import config
from tgbot.handlers import common, create_order, admin
from tgbot.middlewares.common_mw import RegistrationUsers, AdminsIDs, CallbackQueryAnswer, ConnectionController
from tgbot.filters.create_order_filters import ListStateFilter
from tgbot.filters.admin_filters import IsAdmin
from tgbot.database.models import ConnectionPool

def register_middlewares(dp: Dispatcher):
    conn_pull = ConnectionPool()
    dp.setup_middleware(ConnectionController(con_pull=conn_pull))
    dp.setup_middleware(RegistrationUsers())
    dp.setup_middleware(AdminsIDs())
    dp.setup_middleware(CallbackQueryAnswer())
    pass

def register_filters(dp: Dispatcher):
    dp.bind_filter(ListStateFilter)
    dp.bind_filter(IsAdmin)
    pass

def register_handlers(dp: Dispatcher):
    create_order.handlers_registration(dp)
    admin.hendler_registration(dp)
    common.hendlers_registration(dp)
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
# университеты, предметы и преподы по умолчанию, возможно хранить в базу данных
