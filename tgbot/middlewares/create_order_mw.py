from aiogram import types
from aiogram.dispatcher import filters
from aiogram.dispatcher.handler import CancelHandler, SkipHandler, current_handler
from aiogram.dispatcher.middlewares import BaseMiddleware, LifetimeControllerMiddleware


from tgbot.keyboards.reply_kb import make_registration_kb
from tgbot.FSMStates.client_st import FSMRegistration
