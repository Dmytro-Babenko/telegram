from aiogram.dispatcher.filters.state import State, StatesGroup

class FSMAdding(StatesGroup):
    # adding_way = State()
    category = State()
    name = State()
    kind = State()
    confirmation = State()
    
class FSMTypeAdding(FSMAdding):
    category = State()
    name = State()
    kind = State()
    confirmation = State()

class FSMAddingType(FSMAdding):
    kind = State()

