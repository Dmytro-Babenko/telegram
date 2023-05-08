from aiogram import types
from aiogram.dispatcher import filters
from aiogram.dispatcher.handler import CancelHandler, SkipHandler, ctx_data, current_handler
from aiogram.dispatcher.middlewares import BaseMiddleware, LifetimeControllerMiddleware


from tgbot.keyboards.reply_kb import make_registration_kb
from tgbot.FSMStates.client_st import FSMRegistration
from tgbot.database.models import Client, DBWorker, ConnectionPool

admins = [{'username': 'Dmitriy_babenko87'}]
# contacts = {}

class RegistrationUsers(BaseMiddleware):

    async def on_pre_process_message(self, message: types.Message, data: dict):
        client_id = message.from_user.id
        db_worker = data.get('db_worker')
        contacts = db_worker.load_all(Client)
        if client_id not in contacts and not message.contact:
            await FSMRegistration.contact.set()
            kb = make_registration_kb()
            await message.answer('Ви не зареєстровані, надішліть, будь ласка, свій контакт', reply_markup=kb)
            raise CancelHandler

class AdminsIDs(BaseMiddleware):
    async def on_process_message(self, message:types.Message, data:dict):
        handler = current_handler.get()
        need_admin = getattr(handler, 'need_admins', False)
        if need_admin:
            data['admin'] = admins[0]['username']

class CallbackQueryAnswer(BaseMiddleware):
    async def on_post_process_callback_query(self, cq:types.CallbackQuery, data_from_filter:list, data:dict):
        await cq.answer()

class ConnectionController(BaseMiddleware):
    def __init__(self, con_pull: ConnectionPool):
        self._con_pull = con_pull
        super().__init__()

    def create_db_worker(self):
        return DBWorker(self._con_pull.get_conn())
    
    def close_db_worker(self, db_worker):
        if db_worker:
            self._con_pull.put_conn(db_worker.conn)

    async def on_pre_process_message(self, message: types.Message, data: dict):
        # print(self._con_pull.get_conn(), self._con_pull._pull.qsize())
        data['db_worker'] = self.create_db_worker()
    
    async def on_post_process_message(self, message: types.Message, data_fron_hendler, data: dict):
        self.close_db_worker(data.get('db_worker'))

    async def on_pre_process_callback_query(self, cq: types.CallbackQuery, data: dict):
        data['db_worker'] = self.create_db_worker()
    
    async def on_post_process_callback_query(self, cq: types.CallbackQuery, data_fron_hendler, data: dict):
        self.close_db_worker(data.get('db_worker'))

    async def on_pre_process_inline_query(self, inline_query: types.InlineQuery, data: dict):
        print('a')
        data['db_worker'] = self.create_db_worker()
    
    async def on_post_process_inline_query(self, inline_query: types.InlineQuery, data_fron_hendler, data: dict):
        self.close_db_worker(data.get('db_worker'))

