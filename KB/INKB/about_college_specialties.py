from aiogram.utils.keyboard import InlineKeyboardBuilder

from TEXT.about_college.txt import specialties_text


def specialties_kb(lang, level='main'):
    builder = InlineKeyboardBuilder()
    buttons = specialties_text[lang]['buttons']

    if level == 'main':
        builder.button(text=buttons['it'], callback_data='college_spec:it')
        builder.button(text=buttons['business'], callback_data='college_spec:business')
        builder.button(text=buttons['design'], callback_data='college_spec:design')
        builder.adjust(1)
    else:
        builder.button(text=buttons['back'], callback_data='college_spec:main')

    return builder.as_markup()
