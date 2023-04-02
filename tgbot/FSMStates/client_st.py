from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

class FSMRegistration(StatesGroup):
    contact = State()

class FSMCreateOrder(StatesGroup):
    type_order = State()
    subject = State()
    date = State()
    time = State()
    university = State()
    files = State()

