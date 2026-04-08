from aiogram.types import CallbackQuery, Message, Contact
from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from servers import get_active_important_events, get_important_event_by_id, get_user_language
from KB.RPKB.about_college_rpkb import about_college
from KB.RPKB.menu_adnis import admis_menu
from TEXT.menu import start_menu_txt,start_menu_code
from TEXT.choose import Welcom_txt
from TEXT.contacts import Contacts_txt
from KB.RPKB.about_cons import con_kb
from KB.INKB.admin_cons import build_user_event_card_kb, build_user_events_list_kb
from aiogram.fsm.scene import StateFilter
from TEXT.lang_change import language_buttons
from TEXT.events_txt import events_txt
from aiogram.types import ReplyKeyboardRemove
from KB.INKB.choose_lang import lang_choose_inkb
from utils import build_event_text
router = Router()
all_words = [main for i in start_menu_txt.values() for main in i.values()]


async def send_important_events(target, user_id, edit=False):
    lang = get_user_language(user_id) or 'RU'
    events = get_active_important_events()
    if not events:
        if edit:
            try:
                await target.edit_text(text=events_txt[lang]['empty'], reply_markup=None)
            except TelegramBadRequest as e:
                if "message is not modified" not in str(e):
                    raise
            return
        await target.answer(text=events_txt[lang]['empty'], reply_markup=None)
        return
    if edit:
        try:
            await target.edit_text(
                text=events_txt[lang]['title'],
                reply_markup=build_user_events_list_kb(events),
            )
        except TelegramBadRequest as e:
            if "message is not modified" not in str(e):
                raise
        return
    await target.answer(
        text=events_txt[lang]['title'],
        reply_markup=build_user_events_list_kb(events),
    )


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
        await send_important_events(message, user_id)
    elif text in start_menu_code['admis'][lang]:
        await message.answer(text=Welcom_txt['admis'][lang], reply_markup=admis_menu(user_id))
    elif text in start_menu_code['contacts'][lang]:
        await message.answer(text=Contacts_txt[lang], reply_markup=None)
    elif text in start_menu_code['change_lang'][lang]:
        await message.answer(text='...', reply_markup=ReplyKeyboardRemove())
        await message.answer(text=language_buttons[lang]['change_language']['frs_m'], reply_markup=lang_choose_inkb())
    else:
        await message.answer(text='еror')


@router.callback_query(F.data == 'important_events')
async def important_events_callback(callback: CallbackQuery):
    if callback.message is None:
        await callback.answer()
        return
    await send_important_events(callback.message, callback.from_user.id, edit=True)
    await callback.answer()


@router.callback_query(F.data.startswith('important_event:'))
async def important_event_detail_callback(callback: CallbackQuery):
    if callback.message is None:
        await callback.answer()
        return

    event_id = int(callback.data.split(':')[1])
    event = get_important_event_by_id(event_id)
    if event is None or not event[6]:
        await callback.answer(events_txt[get_user_language(callback.from_user.id) or 'RU']['empty'], show_alert=True)
        return

    lang = get_user_language(callback.from_user.id) or 'RU'
    try:
        await callback.message.edit_text(
            text=build_event_text(lang, event, events_txt),
            reply_markup=build_user_event_card_kb(event_id, event[4], event[5]),
        )
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise
    await callback.answer()
