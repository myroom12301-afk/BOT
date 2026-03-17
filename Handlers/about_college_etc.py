from aiogram.types import Message
from aiogram import F, Router
from servers import get_user_language
from TEXT.about_college.about_college_menu import college_menu_txt
from TEXT.about_college.txt import college_menu_info, back
from KB.RPKB.start_menu import start__menu
from aiogram.fsm.scene import StateFilter
router = Router()

all_menu_texts = [menu for i in college_menu_txt.values() for menu in i.values()]


@router.message(F.text.in_(all_menu_texts),StateFilter(None))
async def college_menu(message: Message):
    user_id = message.from_user.id
    lang = get_user_language(user_id)
    if message.text in ('🔙 Назад', '🔙 Back', '🔙 Артка'):
        await message.answer(text=back[lang], reply_markup=start__menu(user_id))
    else:
        await message.answer(text=college_menu_info[lang][message.text]['text'])
