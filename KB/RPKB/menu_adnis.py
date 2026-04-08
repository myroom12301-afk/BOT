from aiogram.utils.keyboard import ReplyKeyboardBuilder
from servers import get_user_language
from TEXT.about_admis.admis_menu import admis_menu_txt

def admis_menu(user_id):
    lang = get_user_language(user_id)
    builder = ReplyKeyboardBuilder()
    keys = ['dates', 'type', 'docs', 'price', 'faq', 'back']
    for i in keys:
        builder.button(text=admis_menu_txt[lang][i])
    builder.adjust(3)
    return builder.as_markup(resize_keyboard = True, adjust=True)
