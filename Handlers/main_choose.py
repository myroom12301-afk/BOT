from aiogram.types import Message, Contact
from aiogram import F, Router
from servers import get_active_important_events, get_user_language
from KB.RPKB.about_college_rpkb import about_college
from KB.RPKB.menu_adnis import admis_menu
from TEXT.menu import start_menu_txt,start_menu_code
from TEXT.choose import Welcom_txt
from TEXT.contacts import Contacts_txt
from TEXT.faq import faq_txt
from KB.RPKB.about_cons import con_kb
from KB.INKB.admin_cons import build_event_link_kb
from aiogram.fsm.scene import StateFilter
from TEXT.lang_change import language_buttons
from TEXT.events_txt import events_txt
from aiogram.types import ReplyKeyboardRemove
from KB.INKB.choose_lang import lang_choose_inkb
from utils import build_event_text
router = Router()
all_words = [main for i in start_menu_txt.values() for main in i.values()]
@router.message(F.text.in_(all_words), StateFilter(None))
async def college(message: Message):
    user_id = message.from_user.id
    lang = get_user_language(user_id)
    text = message.text
    if text in start_menu_code['info'][lang]:
        await message.answer(text=Welcom_txt['info'][lang], reply_markup=about_college(user_id))
    elif text in start_menu_code['cons'][lang]:
        await message.answer(text=Welcom_txt['cons'][lang], reply_markup=con_kb(user_id))
    elif text in start_menu_code['events'][lang]:
        events = get_active_important_events()
        if not events:
            await message.answer(text=events_txt[lang]['empty'], reply_markup=None)
            return
        await message.answer(text=events_txt[lang]['title'], reply_markup=None)
        for event in events:
            await message.answer(
                text=build_event_text(lang, event, events_txt),
                reply_markup=build_event_link_kb(event[4], event[5]),
            )
    elif text in start_menu_code['admis'][lang]:
        await message.answer(text=Welcom_txt['admis'][lang], reply_markup=admis_menu(user_id))
    elif text in start_menu_code['contacts'][lang]:
        await message.answer(text=Contacts_txt[lang], reply_markup=None)
    elif text in start_menu_code['FAQ'][lang]:
        await message.answer(text=faq_txt[lang], reply_markup=None)
    elif text in start_menu_code['change_lang'][lang]:
        await message.answer(text='...', reply_markup=ReplyKeyboardRemove())
        await message.answer(text=language_buttons[lang]['change_language']['frs_m'], reply_markup=lang_choose_inkb())
    else:
        await message.answer(text='еror')
