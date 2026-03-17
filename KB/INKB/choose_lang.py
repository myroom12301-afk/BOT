from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.keyboard import InlineKeyboardButton
def lang_choose_inkb():
    builder = InlineKeyboardBuilder()
    builder.button(text="🇰🇬", callback_data='KY')
    builder.button(text='🇷🇺', callback_data='RU')
    builder.button(text='🇬🇧', callback_data='EN')
    builder.adjust(3)
    return builder.as_markup()