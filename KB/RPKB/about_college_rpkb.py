from aiogram.utils.keyboard import ReplyKeyboardBuilder
from servers import get_user_language
from TEXT.about_college.about_college_menu import college_menu_txt

def about_college(user_id):
    lang = get_user_language(user_id)
    builder = ReplyKeyboardBuilder()
    keys = ['info', 'spec', 'life', 'opp', 'loc', 'back']
    for i in keys:
        builder.button(text=college_menu_txt[lang][i])
    builder.adjust(3)
    return builder.as_markup(resize_keyboard=True, adjust=True)