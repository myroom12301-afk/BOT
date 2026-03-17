from aiogram.types import Message
from aiogram import Router,F
from TEXT.FIRST_MESSAGE.Welcome import First_welcome
from servers import get_user_language, init_db
from KB.INKB.choose_lang import lang_choose_inkb
from TEXT.FIRST_MESSAGE.first_Message import lange  as lan
from KB.RPKB.start_menu import start__menu
import asyncio
from aiogram.fsm.scene import StateFilter
router = Router()

@router.message(F.text == '/start', StateFilter(None))
async def start(m: Message):
    user_id = m.from_user.id
    init_db()
    lang = get_user_language(user_id)
    if lang is None:
        await m.answer(First_welcome)
        await asyncio.sleep(1)
        await m.answer(text='Выберите язык👇', reply_markup=lang_choose_inkb())

    else:
        await m.answer(text=lan[lang]['select_language'])
        await asyncio.sleep(1)
        await m.answer(text=lan[lang]['menu_open'], reply_markup=start__menu(user_id))