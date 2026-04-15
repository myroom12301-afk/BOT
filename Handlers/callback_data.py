import logging

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from FSM import Form
from KB.INKB.cons import get_calendar
from KB.RPKB.about_cons import con_kb
from KB.RPKB.start_menu import start__menu
from TEXT.cons_txt import record_buttons
from TEXT.FIRST_MESSAGE.first_Message import lange
from TEXT.delete_user_cons import delete_record_txt
from servers import add_user, get_user_language, del_cons, get_user_active_booking
from utils import safe_delete, safe_edit_text, send_email

con_time = ['10:00', '12:00', '14:00', '16:00']
router = Router()


@router.callback_query(F.data.in_(['KY', 'RU', 'EN']), StateFilter(None))
async def add__user(cb: CallbackQuery):
    await cb.answer()
    user_id = cb.from_user.id
    add_user(user_id, cb.data)
    await safe_edit_text(cb.message, text=lange[cb.data]['select_language'], reply_markup=None)
    await cb.message.answer(text=lange[cb.data]['menu_open'], reply_markup=start__menu(user_id))


@router.callback_query(F.data == 'back_')
async def back(cb: CallbackQuery, state: FSMContext):
    user_id = cb.from_user.id
    lang = get_user_language(user_id)
    await safe_delete(cb.message)
    await state.clear()
    await cb.message.answer(
        text=record_buttons[lang]['back']['frs_m'],
        reply_markup=con_kb(user_id)
    )
    await cb.answer()


@router.callback_query(F.data == 'back_main')
async def back_main(cb: CallbackQuery, state: FSMContext):
    user_id = cb.from_user.id
    lang = get_user_language(user_id)
    await safe_delete(cb.message)
    await state.clear()
    await cb.message.answer(
        text=record_buttons[lang]['back']['frs_m'],
        reply_markup=start__menu(user_id)
    )
    await cb.answer()


@router.callback_query(F.data == 'DEL')
async def del_cone(cb: CallbackQuery):
    user_id = cb.from_user.id
    lang = get_user_language(user_id)
    booking = get_user_active_booking(user_id)
    deleted = del_cons(user_id)
    await safe_delete(cb.message)
    if deleted:
        await cb.message.answer(text=delete_record_txt[lang]['success_msg'])
        _, name, who, phone, slot_date, slot_time = booking
        body = (
            f" Данные пользователя:"
            f"\nИмя: {name}"
            f"\nТелефон: {phone}"
            f"\nДата: {slot_date}"
            f"\nВремя: {slot_time}"
            f"\nФормат: {who}"
        )
        try:
            send_email(subject="Запись на консультацию была удалена.", body=body)
        except Exception:
            logging.exception("Не удалось отправить письмо об удалении записи")
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

    await safe_delete(cb.message)
    await state.clear()
    await state.update_data(edit_cons_id=booking[0])
    await cb.message.answer(text=record_buttons[lang]['sign_up']['edit_frs_m'])
    await cb.message.answer(
        text=record_buttons[lang]['steps']['data'],
        reply_markup=get_calendar(user_id, excluded_cons_id=booking[0])
    )
    await state.set_state(Form.date)
    await cb.answer()
