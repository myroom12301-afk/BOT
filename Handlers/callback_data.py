
from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery

from KB.RPKB.start_menu import start__menu

from KB.RPKB.about_cons import con_kb
from KB.INKB.cons import get_calendar
from TEXT.cons_txt import record_buttons
from TEXT.FIRST_MESSAGE.first_Message import lange
from TEXT.delete_user_cons import delete_record_txt
from FSM import Form
from servers import add_user
from servers import get_user_language
from aiogram.fsm.scene import StateFilter

from servers import del_cons, get_user_active_booking
from aiogram.fsm.context import FSMContext
con_time = ['10:00', '12:00', '14:00', '16:00']
router = Router()
@router.callback_query(F.data.in_(['KY','RU','EN']), StateFilter(None))
async def add__user(cb: CallbackQuery):
    await cb.answer()
    user_id = cb.from_user.id
    add_user(user_id, cb.data)
    try:
        await cb.message.edit_text(text=lange[cb.data]['select_language'], reply_markup=None)
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise
    await cb.message.answer(text=lange[cb.data]['menu_open'],reply_markup=start__menu(user_id))
@router.callback_query(F.data=='back_')
async def back(cb: CallbackQuery,state: FSMContext):
    user_id = cb.from_user.id
    lang = get_user_language(user_id)
    await cb.message.delete()
    await state.clear()
    await cb.message.answer(
        text=record_buttons[lang]['back']['frs_m'],
        reply_markup=con_kb(user_id)
    )

    await cb.answer()

@router.callback_query(F.data=='back_main')
async def back_main(cb: CallbackQuery, state: FSMContext):
    user_id = cb.from_user.id
    lang = get_user_language(user_id)
    await cb.message.delete()
    await state.clear()
    await cb.message.answer(
        text=record_buttons[lang]['back']['frs_m'],
        reply_markup=start__menu(user_id)
    )
    await cb.answer()

@router.callback_query(F.data=='DEL')
async def del_cone(cb: CallbackQuery):
    user_id = cb.from_user.id
    lang = get_user_language(user_id)
    deleted = del_cons(user_id)
    await cb.message.delete()
    if deleted:
        await cb.message.answer(text=delete_record_txt[lang]['success_msg'])
    else:
        await cb.message.answer(text=delete_record_txt[lang]['already_deleted'])
    await cb.answer()


@router.callback_query(F.data == 'EDIT')
async def edit_cons(cb: CallbackQuery, state: FSMContext):
    user_id = cb.from_user.id
    lang = get_user_language(user_id)
    booking = get_user_active_booking(user_id)

    if booking is None:
        await cb.answer(delete_record_txt[lang]['edit_unavailable'], show_alert=True)
        return

    await cb.message.delete()
    await state.clear()
    await state.update_data(edit_cons_id=booking[0])
    await cb.message.answer(text=record_buttons[lang]['sign_up']['edit_frs_m'])
    await cb.message.answer(
        text=record_buttons[lang]['steps']['data'],
        reply_markup=get_calendar(user_id, excluded_cons_id=booking[0])
    )
    await state.set_state(Form.date)
    await cb.answer()
