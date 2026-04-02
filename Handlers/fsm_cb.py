import asyncio

from aiogram import F, Router
from aiogram.types import Message


from FSM import Form

from KB.RPKB.about_cons import con_kb
from KB.INKB.cons import inkb_who, cons_time
from KB.INKB.conf import confim_kb


from TEXT.cons_txt import record_buttons, fields

from servers import get_user_language, add_cons

from utils import is_valid_phone


con_time = ['10:00', '12:00', '14:00', '16:00']
router = Router()
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext


def build_cons_preview(lang, data):
    return (
        f"{fields[lang]['name']}: {data.get('name')}\n"
        f"{fields[lang]['who']}: {data.get('who')}\n"
        f"{fields[lang]['phone']}: {data.get('number')}\n"
        f"{fields[lang]['date']}: {data.get('date')}\n"
        f"{fields[lang]['time']}: {data.get('meet_time')}"
    )

@router.callback_query(F.data.in_(con_time))
async def ad(cb: CallbackQuery, state: FSMContext):
    user_id = cb.from_user.id
    lang = get_user_language(user_id)
    await state.update_data(meet_time=cb.data)
    await cb.message.delete()
    await cb.message.answer(
        text=record_buttons[lang]['steps']['who'],
        reply_markup=inkb_who(user_id)
    )
    await cb.answer()


@router.callback_query(F.data.in_(["Student", "Parent"]))
async def who_fun(cb: CallbackQuery, state: FSMContext):
    user_id = cb.from_user.id
    lang = get_user_language(user_id)

    await state.update_data(who=cb.data)
    await state.set_state(Form.name)
    await cb.message.delete()
    await cb.message.answer(text=record_buttons[lang]['steps']['name'])
    await cb.answer()
@router.message(Form.name)
async def name(m: Message, state: FSMContext):
    user_id = m.from_user.id
    lang = get_user_language(user_id)
    if m.text.replace(" ", "").isalpha():
        await state.update_data(name=m.text)
        await state.set_state(Form.number)
        await m.answer(text=record_buttons[lang]['steps']['phone'])
    else:
        await m.answer(text=record_buttons[lang]['steps']['name'])

@router.message(Form.number)
async def phone(m: Message, state: FSMContext):
    user_id = m.from_user.id
    lang = get_user_language(user_id)
    if not is_valid_phone(m.text):
        await m.delete()
        await m.answer(text=record_buttons[lang]['steps']['phone_error'])
        return
    await m.delete()
    await state.update_data(number=m.text)
    await state.set_state(Form.conf)
    data = await state.get_data()
    await m.answer(text=record_buttons[lang]['steps']['confirm'])

    await asyncio.sleep(1)
    await m.answer(text=build_cons_preview(lang, data), reply_markup=confim_kb(lang))

@router.callback_query(F.data.startswith("date_"))
async def process_date(cb: CallbackQuery, state: FSMContext):
    selected_date = cb.data.split("_")[1]
    user_id = cb.from_user.id
    lang = get_user_language(user_id)
    data = await state.get_data()
    await state.update_data(date=selected_date)
    await cb.message.delete()
    await cb.message.answer(
        text=record_buttons[lang]['steps']['time'],
        reply_markup=cons_time(user_id, selected_date, data.get('edit_cons_id'))
    )
    await state.set_state(Form.meet_time)
    await cb.answer()

@router.message(Form.conf)
async def block_text_on_confirm(message: Message):
    user_id = message.from_user.id
    lang = get_user_language(user_id)
    await message.answer(text=record_buttons[lang]['steps']['confirm_pointer'])


@router.callback_query(F.data=='conf')
async def confirm(cb: CallbackQuery, state: FSMContext):
    user_id = cb.from_user.id
    lang = get_user_language(user_id)
    data = await state.get_data()
    result = add_cons(data, user_id, data.get('edit_cons_id'))

    if result == 'slot_taken':
        await cb.message.delete()
        await cb.message.answer(text=record_buttons[lang]['steps']['slot_taken'])
        await cb.message.answer(
            text=record_buttons[lang]['steps']['time'],
            reply_markup=cons_time(user_id, data.get('date'), data.get('edit_cons_id'))
        )
        await state.set_state(Form.meet_time)
        await cb.answer()
        return

    if result == 'has_active':
        await cb.message.delete()
        await cb.message.answer(text=record_buttons[lang]['sign_up']['already_have'])
        await cb.message.answer(text=record_buttons[lang]['back']['frs_m'], reply_markup=con_kb(user_id))
        await state.clear()
        await cb.answer()
        return

    if result == 'missing_old':
        await cb.message.delete()
        await cb.message.answer(text=record_buttons[lang]['view_records']['no_record'])
        await cb.message.answer(text=record_buttons[lang]['back']['frs_m'], reply_markup=con_kb(user_id))
        await state.clear()
        await cb.answer()
        return

    await cb.message.delete()
    await cb.message.answer(
        text=record_buttons[lang]['steps']['edit_success']
        if data.get('edit_cons_id') is not None
        else record_buttons[lang]['steps']['success']
    )
    await asyncio.sleep(1)
    await cb.message.answer(text=record_buttons[lang]['back']['frs_m'], reply_markup=con_kb(user_id))
    await state.clear()

    await cb.answer()
