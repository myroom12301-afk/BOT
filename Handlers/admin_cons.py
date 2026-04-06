from datetime import datetime

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from FSM import Form
from KB.INKB.admin_cons import (
    build_admin_cons_card_kb,
    build_admin_event_confirm_kb,
    build_admin_cons_list_kb,
    build_admin_event_card_kb,
    build_admin_events_list_kb,
)
from TEXT.admin_cons_text import admin_cons_text, booking_confirmed_user_text
from TEXT.events_txt import events_txt
from config import ADMIN_IDS
from servers import (
    add_important_event,
    deactivate_important_event,
    get_active_consultations_count,
    get_active_consultations_page,
    get_active_important_events,
    get_consultation_by_id,
    get_important_event_by_id,
    get_unique_user_ids,
    get_user_language,
    update_consultation_status,
)
from utils import build_event_text

router = Router()
PAGE_SIZE = 5
ADMIN_EVENT_STATES = (
    Form.event_title,
    Form.event_date,
    Form.event_description,
    Form.event_link,
    Form.event_button_text,
    Form.event_confirm,
)


def is_admin(user_id):
    return user_id in ADMIN_IDS


def format_full_date(slot_date):
    try:
        return datetime.strptime(slot_date, '%Y-%m-%d').strftime('%d.%m.%Y')
    except ValueError:
        return slot_date


async def get_callback_message(callback: CallbackQuery):
    message = callback.message
    if message is None:
        await callback.answer(admin_cons_text['message_not_available'], show_alert=True)
        return None
    return message


async def send_admin_cons_page(target, page):
    total_count = get_active_consultations_count()
    if total_count == 0:
        await target.answer(admin_cons_text['empty'])
        return

    bookings = get_active_consultations_page(page=page, page_size=PAGE_SIZE)
    has_next_page = total_count > page * PAGE_SIZE
    await target.answer(
        admin_cons_text['list_title'].format(page=page),
        reply_markup=build_admin_cons_list_kb(bookings, page, has_next_page),
    )


async def send_admin_events_list(target, edit=False):
    events = get_active_important_events()
    text = admin_cons_text['events_title'] if events else admin_cons_text['events_empty']
    reply_markup = build_admin_events_list_kb(events)
    if edit:
        try:
            await target.edit_text(text, reply_markup=reply_markup)
        except TelegramBadRequest as e:
            if "message is not modified" not in str(e):
                raise
        return
    await target.answer(text, reply_markup=reply_markup)


async def notify_users_about_important_event(bot, title, event_date=None):
    for user_id in get_unique_user_ids():
        lang = get_user_language(user_id) or 'RU'
        text = f"{events_txt[lang]['notification_title']}\n\n{title}"
        if event_date:
            text += f"\n{events_txt[lang]['event_date']}: {format_full_date(event_date)}"
        text += f"\n\n{events_txt[lang]['notification_open']}"
        try:
            await bot.send_message(user_id, text)
        except TelegramForbiddenError:
            pass
        except TelegramBadRequest:
            pass
        except Exception:
            pass


async def send_event_publish_preview(message: Message, state: FSMContext):
    data = await state.get_data()
    preview_event = (
        0,
        data['title'],
        data['event_date'],
        data['description'],
        data.get('link'),
        data.get('button_text'),
        1,
    )
    await message.answer(
        f"{admin_cons_text['event_confirm_step']}\n\n{build_event_text('RU', preview_event, events_txt)}",
        reply_markup=build_admin_event_confirm_kb(),
    )


def build_card_text(booking):
    cons_id, name, phone, user_id, slot_date, slot_time, status = booking
    return (
        f"{admin_cons_text['card_title'].format(id=cons_id)}\n\n"
        f"{admin_cons_text['name']}: {name if str(name).strip() else admin_cons_text['no_name']}\n"
        f"{admin_cons_text['phone']}: {phone if str(phone).strip() else '-'}\n"
        f"{admin_cons_text['user_id']}: {user_id}\n"
        f"{admin_cons_text['date']}: {format_full_date(slot_date)}\n"
        f"{admin_cons_text['time']}: {slot_time}\n"
        f"{admin_cons_text['status']}: {status}"
    )


async def render_first_admin_page(message):
    bookings = get_active_consultations_page(page=1, page_size=PAGE_SIZE)
    total_count = get_active_consultations_count()

    if total_count == 0:
        try:
            await message.edit_text(admin_cons_text['empty'])
        except TelegramBadRequest as e:
            if "message is not modified" not in str(e):
                raise
        return

    try:
        await message.edit_text(
            admin_cons_text['list_title'].format(page=1),
            reply_markup=build_admin_cons_list_kb(
                bookings,
                page=1,
                has_next_page=total_count > PAGE_SIZE,
            ),
        )
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise


async def render_admin_event_card(message, event_id):
    event = get_important_event_by_id(event_id)
    if event is None or not event[6]:
        await message.edit_text(
            admin_cons_text['event_not_found'],
            reply_markup=build_admin_events_list_kb(get_active_important_events()),
        )
        return False
    lang = get_user_language(message.chat.id) or 'RU'
    await message.edit_text(
        build_event_text(lang, event, events_txt),
        reply_markup=build_admin_event_card_kb(event_id, event[4], event[5]),
    )
    return True


@router.message(Command('admin_cons'))
async def admin_cons_command(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer(admin_cons_text['access_denied'])
        return

    await send_admin_cons_page(message, page=1)


@router.message(Command('admin_events'))
async def admin_events_command(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await message.answer(admin_cons_text['access_denied'])
        return

    await state.clear()
    await send_admin_events_list(message)


@router.callback_query(F.data.startswith('admin_cons_page:'))
async def admin_cons_page_callback(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer(admin_cons_text['access_denied'], show_alert=True)
        return

    message = await get_callback_message(callback)
    if message is None:
        return

    page = int(callback.data.split(':')[1])
    bookings = get_active_consultations_page(page=page, page_size=PAGE_SIZE)
    total_count = get_active_consultations_count()

    if total_count == 0:
        try:
            await message.edit_text(admin_cons_text['empty'])
        except TelegramBadRequest as e:
            if "message is not modified" not in str(e):
                raise
        await callback.answer()
        return

    has_next_page = total_count > page * PAGE_SIZE
    try:
        await message.edit_text(
            admin_cons_text['list_title'].format(page=page),
            reply_markup=build_admin_cons_list_kb(bookings, page, has_next_page),
        )
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise
    await callback.answer()


@router.callback_query(F.data.startswith('admin_cons:'))
async def admin_cons_detail_callback(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer(admin_cons_text['access_denied'], show_alert=True)
        return

    message = await get_callback_message(callback)
    if message is None:
        return

    cons_id = int(callback.data.split(':')[1])
    booking = get_consultation_by_id(cons_id)

    if booking is None:
        await callback.answer(admin_cons_text['booking_not_found'], show_alert=True)
        return

    try:
        await message.edit_text(
            build_card_text(booking),
            reply_markup=build_admin_cons_card_kb(cons_id),
        )
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise
    await callback.answer()


@router.callback_query(F.data == 'admin_cons_back')
async def admin_cons_back_callback(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer(admin_cons_text['access_denied'], show_alert=True)
        return

    message = await get_callback_message(callback)
    if message is None:
        return

    await render_first_admin_page(message)
    await callback.answer()


@router.callback_query(F.data == 'admin_event_back')
async def admin_event_back_callback(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer(admin_cons_text['access_denied'], show_alert=True)
        return

    message = await get_callback_message(callback)
    if message is None:
        return

    await state.clear()
    await send_admin_events_list(message, edit=True)
    await callback.answer()


@router.callback_query(F.data.startswith('admin_event:'))
async def admin_event_detail_callback(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer(admin_cons_text['access_denied'], show_alert=True)
        return

    message = await get_callback_message(callback)
    if message is None:
        return

    event_id = int(callback.data.split(':')[1])
    if not await render_admin_event_card(message, event_id):
        await callback.answer(admin_cons_text['event_not_found'], show_alert=True)
        return
    await callback.answer()


@router.callback_query(F.data == 'admin_event_add')
async def admin_event_add_callback(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer(admin_cons_text['access_denied'], show_alert=True)
        return

    message = await get_callback_message(callback)
    if message is None:
        return

    await state.clear()
    await state.set_state(Form.event_title)
    await message.answer(admin_cons_text['event_title_step'])
    await callback.answer()


@router.message(Form.event_title)
async def admin_event_title_step(message: Message, state: FSMContext):
    title = message.text.strip()
    if not title:
        await message.answer(admin_cons_text['event_title_step'])
        return
    await state.update_data(title=title)
    await state.set_state(Form.event_date)
    await message.answer(admin_cons_text['event_date_step'])


@router.message(Form.event_date)
async def admin_event_date_step(message: Message, state: FSMContext):
    try:
        datetime.strptime(message.text.strip(), '%Y-%m-%d')
    except ValueError:
        await message.answer(admin_cons_text['event_date_error'])
        return
    await state.update_data(event_date=message.text.strip())
    await state.set_state(Form.event_description)
    await message.answer(admin_cons_text['event_description_step'])


@router.message(Form.event_description)
async def admin_event_description_step(message: Message, state: FSMContext):
    await state.update_data(description=message.text.strip())
    await state.set_state(Form.event_link)
    await message.answer(admin_cons_text['event_link_step'])


@router.message(Form.event_link, Command('skip'))
async def admin_event_skip_link(message: Message, state: FSMContext):
    await state.update_data(link=None)
    await state.set_state(Form.event_button_text)
    await message.answer(admin_cons_text['event_button_text_step'])


@router.message(Form.event_link)
async def admin_event_link_step(message: Message, state: FSMContext):
    await state.update_data(link=message.text.strip())
    await state.set_state(Form.event_button_text)
    await message.answer(admin_cons_text['event_button_text_step'])


@router.message(Form.event_button_text, Command('skip'))
async def admin_event_skip_button_text(message: Message, state: FSMContext):
    await state.update_data(button_text=None)
    await state.set_state(Form.event_confirm)
    await send_event_publish_preview(message, state)


@router.message(Form.event_button_text)
async def admin_event_button_text_step(message: Message, state: FSMContext):
    await state.update_data(button_text=message.text.strip() if (await state.get_data()).get('link') else None)
    await state.set_state(Form.event_confirm)
    await send_event_publish_preview(message, state)


@router.callback_query(F.data == 'admin_event_publish')
async def admin_event_publish_callback(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer(admin_cons_text['access_denied'], show_alert=True)
        return

    message = await get_callback_message(callback)
    if message is None:
        return

    current_state = await state.get_state()
    data = await state.get_data()
    required_fields = ('title', 'event_date', 'description')
    if current_state != Form.event_confirm.state or any(not data.get(field) for field in required_fields):
        await callback.answer("Кнопка уже неактуальна", show_alert=True)
        return
    add_important_event(
        data.get('title'),
        data.get('event_date'),
        data.get('description'),
        data.get('link'),
        data.get('button_text'),
    )
    await state.clear()
    await message.answer(admin_cons_text['event_added'])
    await notify_users_about_important_event(callback.bot, data.get('title'), data.get('event_date'))
    await send_admin_events_list(message)
    await callback.answer()


@router.callback_query(F.data == 'admin_event_cancel')
async def admin_event_cancel_callback(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer(admin_cons_text['access_denied'], show_alert=True)
        return

    message = await get_callback_message(callback)
    if message is None:
        return

    await state.clear()
    await message.answer(admin_cons_text['event_publish_canceled'])
    await send_admin_events_list(message)
    await callback.answer()


@router.callback_query(F.data.startswith('admin_cons_done:'))
async def admin_cons_done_callback(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer(admin_cons_text['access_denied'], show_alert=True)
        return

    message = await get_callback_message(callback)
    if message is None:
        return

    cons_id = int(callback.data.split(':')[1])
    booking = get_consultation_by_id(cons_id)
    if booking is None:
        await callback.answer(admin_cons_text['booking_not_found'], show_alert=True)
        return

    updated = update_consultation_status(cons_id, 'done')

    if not updated:
        await callback.answer(admin_cons_text['booking_not_active'], show_alert=True)
        await render_first_admin_page(message)
        return
    try:
        user_lang = get_user_language(booking[3]) or 'RU'
        await callback.bot.send_message(booking[3], booking_confirmed_user_text[user_lang])
    except (TelegramForbiddenError, TelegramBadRequest) as e:
        print(f"Failed to send confirmation to user {booking[3]}: {e}")
    await render_first_admin_page(message)
    await callback.answer(admin_cons_text['booking_confirmed'])


@router.callback_query(F.data.startswith('admin_cons_delete:'))
async def admin_cons_delete_callback(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer(admin_cons_text['access_denied'], show_alert=True)
        return

    message = await get_callback_message(callback)
    if message is None:
        return

    cons_id = int(callback.data.split(':')[1])
    updated = update_consultation_status(cons_id, 'deleted')

    if not updated:
        await callback.answer(admin_cons_text['booking_not_active'], show_alert=True)
        await render_first_admin_page(message)
        return

    await render_first_admin_page(message)
    await callback.answer(admin_cons_text['booking_deleted'])


@router.callback_query(F.data.startswith('admin_event_delete:'))
async def admin_event_delete_callback(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer(admin_cons_text['access_denied'], show_alert=True)
        return

    message = await get_callback_message(callback)
    if message is None:
        return

    event_id = int(callback.data.split(':')[1])
    if not deactivate_important_event(event_id):
        await callback.answer(admin_cons_text['event_not_found'], show_alert=True)
        await send_admin_events_list(message, edit=True)
        return

    await send_admin_events_list(message, edit=True)
    await callback.answer(admin_cons_text['event_deleted'])


@router.callback_query(StateFilter(*ADMIN_EVENT_STATES))
async def ignore_foreign_callbacks_during_admin_event(callback: CallbackQuery):
    await callback.answer()
