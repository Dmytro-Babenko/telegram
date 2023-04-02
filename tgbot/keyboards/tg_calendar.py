import calendar
from datetime import date, timedelta

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.utils.callback_data import CallbackData
from aiogram.types import CallbackQuery

WEEK_DAYS = ('Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Нд')

calendar_callback = CallbackData('simple_calendar', 'act', 'year', 'month', 'day')
class TgCalendar:

    def make_inscription(self, year, month):
        MONTHES = ("Січень", "Лютий", "Березень", 'Квітень', 'Травень', 'Червень', 'Липень', 'Серпень', 'Вересень', 'Жовтень', 'Листопад', 'Грудень')
        return f'{MONTHES[month-1]} {year}'

    async def start_calendar(
            self,
            year: int = date.today().year,
            month: int = date.today().month,
            # day: int = date.today().day
    ):
        
        today = date.today()
        inscription = self.make_inscription(year, month)
        ignore_callback = calendar_callback.new('IGNORE', year, month, 0)
        
        inline_kb = InlineKeyboardMarkup(row_width=7)

        inline_kb.row()
        # if year <= today.year:
        #     inline_kb.insert(InlineKeyboardButton('<<', callback_data=calendar_callback.new('PREV_YEAR',year, month, 1)))
        inline_kb.insert(InlineKeyboardButton(inscription, callback_data=ignore_callback))
        # inline_kb.insert(InlineKeyboardButton('>>', callback_data=calendar_callback.new('NEXT_YEAR',year, month, 1)))

        inline_kb.row()
        for wd in WEEK_DAYS:
            inline_kb.insert(
                InlineKeyboardButton(wd, callback_data=ignore_callback)
            )

        inline_kb.row()
        clndr = calendar.Calendar()
        for day in clndr.itermonthdays(year, month):

            text, cd = (' ', ignore_callback) if day==0 or date(year, month, day) < today else (day, calendar_callback.new('CHOICE', year, month, day))
            inline_kb.insert(InlineKeyboardButton(text=text, callback_data=cd))
            
        inline_kb.row()
        days_in_month = calendar.monthrange(year, month)[1]
        if date(year, month, days_in_month) - timedelta(days_in_month) < today:
            inline_kb.insert(InlineKeyboardButton('', callback_data=ignore_callback))
        else:
            inline_kb.insert(InlineKeyboardButton('<', callback_data=calendar_callback.new('PREV_MONTH', year, month, 1)))
        inline_kb.insert(InlineKeyboardButton('>', callback_data=calendar_callback.new('NEXT_MONTH', year, month, 1)))    
        
        return inline_kb  
    
    async def selection(self, cq:CallbackQuery, data: CallbackData) -> tuple:
        action = data['act']
        year, month, day = [int(x) for x in data.values() if x.isdigit()]
        output = None
        match action:
            # case 'PREV_YEAR':
            #     kb = await self.start_calendar(year-1, month)
            #     await cq.message.edit_reply_markup(kb)
            # case 'NEXT_YEAR':
            #     kb = await self.start_calendar(year+1, month)
            #     await cq.message.edit_reply_markup(kb)
            case 'PREV_MONTH':
                prev_date = date(year, month, day) - timedelta(days=1)
                kb = await self.start_calendar(prev_date.year, prev_date.month)
                await cq.message.edit_reply_markup(kb)
            case 'NEXT_MONTH':
                next_date = date(year, month, day) + timedelta(days=31)
                kb = await self.start_calendar(next_date.year, next_date.month)
                await cq.message.edit_reply_markup(kb)
            case 'CHOICE':
                # await cq.message.delete_reply_markup()
                output = date(year, month, day)
        return output


# clndr = calendar.Calendar()
# for day in calendar.Calendar().itermonthdays2(2023, 3):
#     print(day)


