from aiogram import types
from aiogram.dispatcher import filters
from aiogram.dispatcher.handler import CancelHandler, SkipHandler, current_handler
from aiogram.dispatcher.middlewares import BaseMiddleware, LifetimeControllerMiddleware


from tgbot.keyboards.reply_kb import make_registration_kb
from tgbot.FSMStates.client_st import FSMRegistration

admins = [{'username': 'Dmitriy_babenko87'}]
contacts = {}

class RegistrationUsers(BaseMiddleware):
    async def on_pre_process_message(self, message: types.Message, data: dict):
        client_id = message.from_user.id
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
    async def on_pre_process_callback_query(self, cq:types.CallbackQuery, data:dict):
        await cq.answer()

    