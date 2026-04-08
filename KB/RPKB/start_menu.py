from aiogram.utils.keyboard import ReplyKeyboardBuilder
from TEXT.menu import start_menu_txt
from servers import get_user_language
def start__menu(user_id):
    lang = get_user_language(user_id)
    startmenu = ReplyKeyboardBuilder()
    buttons_texts = [
        'info',
        'cons',
        'events',
        'admis',
        'contacts',
        'change_lang'
    ]
    for keys in buttons_texts:
        startmenu.button(text=start_menu_txt[lang][keys])
    startmenu.adjust(2)
    return startmenu.as_markup(resize_keyboard=True)
