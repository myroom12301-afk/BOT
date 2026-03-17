from aiogram.utils.keyboard import ReplyKeyboardBuilder
from servers import get_user_language
from TEXT.cons_txt import record_buttons
def con_kb(user_id):
    lang = get_user_language(user_id)
    builder = ReplyKeyboardBuilder()
    builder.button(text=record_buttons[lang]['sign_up']['sign'])
    builder.button(text=record_buttons[lang]['view_records']['sign'])
    builder.button(text=record_buttons[lang]['back']['sign'])
    return builder.as_markup(resize_keyboard=True)