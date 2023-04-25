from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import BoundFilter, StateFilter
from aiogram.dispatcher import FSMContext

from tgbot.keyboards.inline_kb import BUTTONS
from tgbot.FSMStates.client_st import FSMCreateOrder
from tgbot.database import models
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
        return False
    
class IsAdmin(BoundFilter):
    def __init__(self) -> None:
        super().__init__()

    async def check(self, obj):
        client_id = obj.from_user.id
        return client_id in models.Admin.get_all_ids()

