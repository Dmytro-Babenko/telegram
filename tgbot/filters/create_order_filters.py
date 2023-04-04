from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import BoundFilter, StateFilter
from aiogram.dispatcher import FSMContext

from tgbot.keyboards.inline_kb import BUTTONS
from tgbot.FSMStates.client_st import FSMCreateOrder
from tgbot.database.data import universities


class ListStateFilter(BoundFilter):
    def __init__(self, state) -> None:
        super().__init__()
        self.state = state

    CATRGORIES = {
        FSMCreateOrder.university: universities
    }

    async def check(self, data):
        category_lst = self.CATRGORIES.get(self.state, False)
        if category_lst:
            return {'variants': category_lst}
        return category_lst
    



a = [1, 2]
print(a[:100])