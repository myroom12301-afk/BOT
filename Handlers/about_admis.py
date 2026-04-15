from TEXT.about_admis.about_admis import admission_menu_info, back
from TEXT.about_admis.admis_menu import admis_menu_txt
from aiogram.types import Message
from aiogram import F, Router
from aiogram.exceptions import TelegramRetryAfter
from servers import get_user_language
from KB.RPKB.start_menu import start__menu
from aiogram.fsm.scene import StateFilter

router = Router()
all_value = [button for i in admis_menu_txt.values() for button in i.values()]


async def safe_answer(message: Message, **kwargs):
    try:
        return await message.answer(**kwargs)
    except TelegramRetryAfter:
        return None

@router.message(F.text.in_(all_value), StateFilter(None))
async def cons_menu(message: Message):
    user_id = message.from_user.id
    lang = get_user_language(user_id)
    if message.text in ['🔙 Back', '🔙 Назад', '🔙 Артка']:
        await safe_answer(message, text=back[lang], reply_markup=start__menu(user_id))
    else:
        await safe_answer(message, text=admission_menu_info[lang][message.text]['text'], parse_mode='HTML')
