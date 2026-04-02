from KB.RPKB.about_cons import con_kb
from aiogram.types import Message
from aiogram import F, Router
from TEXT.cons_txt import record_buttons
from servers import get_user_language, get_user_cons, get_user_active_booking
from KB.RPKB.start_menu import start__menu
from KB.INKB.cons import get_calendar
from aiogram.fsm.scene import StateFilter
from aiogram.fsm.context import FSMContext
from FSM import Form
from KB.INKB.delete_cons import delete_button
router = Router()
all_hand = [
    item['sign']
    for lang in record_buttons.values()
    for item in lang.values()
    if 'sign' in item
]

@router.message(F.text.in_(all_hand), StateFilter(None))
async def cons_h(message: Message, state: FSMContext):
    user_id = message.from_user.id
    lang = get_user_language(user_id)
    if message.text == record_buttons[lang]['sign_up']['sign']:
        from aiogram.types import ReplyKeyboardRemove
        if get_user_active_booking(user_id) is not None:
            await message.answer(text=record_buttons[lang]['sign_up']['already_have'])
            return
        await message.answer(
            text=record_buttons[lang]['sign_up']['frs_m'],
            reply_markup=ReplyKeyboardRemove()
        )
        await message.answer(
            text=record_buttons[lang]['steps']['data'],
            reply_markup=get_calendar(user_id)
        )
        await state.set_state(Form.date)

    elif message.text == record_buttons[lang]['view_records']['sign']:
        await message.answer(text=record_buttons[lang]['view_records']['frs_m'])
        cons_text = get_user_cons(lang, user_id)
        if cons_text == record_buttons[lang]['view_records']['no_record']:
            await message.answer(text=cons_text)
        else:
            await message.answer(
                text=cons_text,
                reply_markup=delete_button(user_id, lang)
            )
    else:
        await message.answer(text=record_buttons[lang]['back']['frs_m'], reply_markup=start__menu(user_id))
