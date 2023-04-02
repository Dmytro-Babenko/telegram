from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import BoundFilter
from aiogram.dispatcher import FSMContext

from tgbot.keyboards.inline_kb import BUTTONS


#попытаться достать стейт с cq
# class IsRightButton(BoundFilter):
#     def __init__(self, dp) -> None:
#         self.dp = dp
#         super().__init__()
#     async def check(self, cq: types.CallbackQuery) -> bool:
#         state = await self.dp.current_state(user=cq.from_user.id).get_state()
#         name=state.split(':')[1]
#         if cq.data in BUTTONS.get(name, []):
#             return True
#         await cq.message.answer('Оберіть з запропонованих варіантів')
#         return False