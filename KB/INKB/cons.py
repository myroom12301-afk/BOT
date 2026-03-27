from aiogram.utils.keyboard import InlineKeyboardBuilder
from servers import get_user_language, get_active_times
from TEXT.cons_txt import record_buttons, who_txt

CON_TIMES = ['10:00', '12:00', '14:00', '16:00']  # Available consultation slots.


def cons_time(user_id, slot_date):
    lang = get_user_language(user_id)
    builder = InlineKeyboardBuilder()
    # Hide times that are already booked for the selected date.
    busy_times = set(get_active_times(slot_date))
    print(busy_times)
    for time_value in CON_TIMES:
        if time_value not in busy_times:
            builder.button(text=time_value, callback_data=time_value)
    builder.button(text=record_buttons[lang]['back']['sign'], callback_data='back_')
    builder.adjust(2)
    return builder.as_markup()

import datetime

def get_calendar(user_id):
    builder = InlineKeyboardBuilder()
    lang = get_user_language(user_id)
    today = datetime.date.today()

    # Keep the keyboard size stable by skipping fully booked dates.
    shown = 0
    checked = 0
    day = today
    max_lookahead = 365  # Prevent infinite loops if everything is booked.

    while shown < 9 and checked < max_lookahead:
        busy_times = get_active_times(str(day))
        if len(busy_times) < len(CON_TIMES):
            builder.button(text=day.strftime("%d.%m"), callback_data=f"date_{day}")
            shown += 1
        day += datetime.timedelta(days=1)
        checked += 1
    builder.button(text=record_buttons[lang]['back']['sign'], callback_data='back_')
    builder.adjust(3)
    return builder.as_markup()


def inkb_who(user_id):
    lang = get_user_language(user_id)
    builder = InlineKeyboardBuilder()
    builder.button(text=who_txt[lang]['prnt'], callback_data='Parent')
    builder.button(text=who_txt[lang]['sdnt'], callback_data='Student')
    return builder.as_markup()
