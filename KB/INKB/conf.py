from aiogram.utils.keyboard import InlineKeyboardBuilder
from TEXT.cons_txt import record_buttons, confirm_kb
def confim_kb(lang):
    builder = InlineKeyboardBuilder()
    builder.button(text=confirm_kb[lang]['confirm'], callback_data='conf')
    builder.button(text=record_buttons[lang]['back']['sign'], callback_data='back_')
    return builder.as_markup()