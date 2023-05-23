from aiogram.dispatcher.handler import ctx_data
from aiogram.dispatcher.filters import BoundFilter


from tgbot.database.models.conection import DBWorker
from tgbot.database.models.fields import Admin
    
class IsAdmin(BoundFilter):
    def __init__(self) -> None:
        super().__init__()

    async def check(self, obj):
        db_worker: DBWorker = ctx_data.get().get('db_worker')
        client_id = obj.from_user.id
        return client_id in db_worker.load_all(Admin)