from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import BoundFilter, StateFilter
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.handler import ctx_data

from tgbot.keyboards.inline_kb import BUTTONS
from tgbot.FSMStates.client_st import FSMCreateOrder
from tgbot.database.models.fields import Client, University
from tgbot.database.models.conection import DBWorker


class ListStateFilter(BoundFilter):
    def __init__(self, dp: Dispatcher, raw_state) -> None:
        super().__init__()
        self.dp = dp
        self.raw_state = raw_state

    CATRGORIES = {
        FSMCreateOrder.university: University
    }

    async def check(self, user):
        db_worker:DBWorker = ctx_data.get().get('db_worker')
        category = self.CATRGORIES.get(self.raw_state)
        if category:
            state = self.dp.current_state()
            data = await state.get_data()
            client: Client = data['client']
            previous_variants = db_worker.load_previous(client.telegram_id, category)
            all_variants = db_worker.load_all(category)
            return {'variants': all_variants, 'prev_variants': previous_variants}
        return False
    


