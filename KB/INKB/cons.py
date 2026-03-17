from aiogram.utils.keyboard import InlineKeyboardBuilder
from servers import get_user_language
from TEXT.cons_txt import record_buttons, who_txt

def cons_time(user_id):
    lang = get_user_language(user_id)
    builder = InlineKeyboardBuilder()
    con_time = ['10:00', '12:00', '14:00', '16:00']
    for i in range(len(con_time)):
        builder.button(text=con_time[i], callback_data=con_time[i])
    builder.button(text=record_buttons[lang]['back']['sign'], callback_data='back_')
    builder.adjust(2)
    return builder.as_markup()

import datetime

def get_calendar(user_id):
    builder = InlineKeyboardBuilder()
    lang = get_user_language(user_id)
    today = datetime.date.today()

    for i in range(9):
        day = today + datetime.timedelta(days=i)
        builder.button(text=day.strftime("%d.%m"), callback_data=f"date_{day}")
    builder.button(text=record_buttons[lang]['back']['sign'], callback_data='back_')
    builder.adjust(3)
    return builder.as_markup()


def inkb_who(user_id):
    lang = get_user_language(user_id)
    builder = InlineKeyboardBuilder()
    builder.button(text=who_txt[lang]['prnt'], callback_data='Parent')
    builder.button(text=who_txt[lang]['sdnt'], callback_data='Student')
    return builder.as_markup()
