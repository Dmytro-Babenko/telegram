from aiogram import Dispatcher
from aiogram.dispatcher.filters.state import State, StatesGroup

class FSMAdding(StatesGroup):
    # adding_way = State()
    category = State()
    name = State()
    kind = State()
    confirmation = State()
    
    @staticmethod
    async def previous() -> str:

        state = Dispatcher.get_current().current_state()
        state_name = await state.get_state()
        data = await state.get_data()

        try:
            previous_step = FSMAdding.states_names.index(state_name) - 1
        except ValueError:
            previous_step = 0

        if previous_step < 0:
            previous_state_name = None
        else:
            previous_state_name = FSMAdding.states[previous_step].state

        if previous_state_name == 'FSMAdding:kind' and data['category'] != 'Тип':
            previous_state_name = FSMAdding.states[previous_step-1].state

        await state.set_state(previous_state_name)
        return previous_state_name



