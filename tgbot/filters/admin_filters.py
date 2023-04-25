from aiogram.dispatcher.filters import BoundFilter

from tgbot.database import models
    
class IsAdmin(BoundFilter):
    def __init__(self) -> None:
        super().__init__()

    async def check(self, obj):
        client_id = obj.from_user.id
        return client_id in models.Admin.get_all_ids()