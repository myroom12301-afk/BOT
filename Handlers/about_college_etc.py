from aiogram.types import CallbackQuery, Message
from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from servers import get_user_language
from TEXT.about_college.about_college_menu import college_menu_txt
from TEXT.about_college.txt import college_menu_info, specialties_text, back
from KB.RPKB.start_menu import start__menu
from KB.INKB.about_college_specialties import specialties_kb
from aiogram.fsm.scene import StateFilter
router = Router()

all_menu_texts = [menu for i in college_menu_txt.values() for menu in i.values()]
spec_texts = {value['spec'] for value in college_menu_txt.values()}


@router.message(F.text.in_(all_menu_texts),StateFilter(None))
async def college_menu(message: Message):
    user_id = message.from_user.id
    lang = get_user_language(user_id)
    if message.text in ('🔙 Назад', '🔙 Back', '🔙 Артка'):
        await message.answer(text=back[lang], reply_markup=start__menu(user_id))
    elif message.text in spec_texts:
        await message.answer(
            text=specialties_text[lang]['main'],
            reply_markup=specialties_kb(lang)
        )
    else:
        await message.answer(text=college_menu_info[lang][message.text]['text'])


@router.callback_query(F.data.startswith('college_spec:'))
async def college_specialties(cb: CallbackQuery):
    user_id = cb.from_user.id
    lang = get_user_language(user_id)
    section = cb.data.split(':', 1)[1]
    text = specialties_text[lang].get(section, specialties_text[lang]['main'])
    level = 'main' if section == 'main' else 'child'

    try:
        await cb.message.edit_text(
            text=text,
            reply_markup=specialties_kb(lang, level)
        )
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise
    await cb.answer()
