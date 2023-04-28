from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import BoundFilter, StateFilter
from aiogram.dispatcher import FSMContext

from tgbot.keyboards.inline_kb import BUTTONS
from tgbot.FSMStates.client_st import FSMCreateOrder
from tgbot.database import models
from tgbot.database.data import universities


class ListStateFilter(BoundFilter):
    def __init__(self, dp: Dispatcher, raw_state) -> None:
        super().__init__()
        self.dp = dp
        self.raw_state = raw_state

    CATRGORIES = {
        FSMCreateOrder.university: models.University
    }

    async def check(self, user):
        category = self.CATRGORIES.get(self.raw_state)
        if category:
            state = self.dp.current_state()
            data = await state.get_data()
            client: models.Client = data['client']
            previous_variants = models.Loader.load_previous(client.telegram_id, category)
            all_variants = models.Loader.load_all(category)
            return {'variants': all_variants, 'prev_variants': previous_variants}
        return False
    
class IsAdmin(BoundFilter):
    def __init__(self) -> None:
        super().__init__()

    async def check(self, obj):
        client_id = obj.from_user.id
        return client_id in models.Loader.load_all(models.Admin)

