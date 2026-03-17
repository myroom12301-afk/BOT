from aiogram.utils.keyboard import InlineKeyboardBuilder
from TEXT.delete_user_cons import delete_record_txt
def delete_button(user_id, lang):
    builder = InlineKeyboardBuilder()
    builder.button(text=delete_record_txt[lang]['delete_btn'], callback_data='DEL')
    return builder.as_markup()