from datetime import datetime

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from KB.INKB.admin_cons import build_admin_cons_card_kb, build_admin_cons_list_kb
from TEXT.admin_cons_text import admin_cons_text, booking_confirmed_user_text
from config import ADMIN_IDS
from servers import (
    get_active_consultations_count,
    get_active_consultations_page,
    get_consultation_by_id,
    get_user_language,
    update_consultation_status,
)

router = Router()
PAGE_SIZE = 5


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


@router.message(Command('admin_cons'))
async def admin_cons_command(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer(admin_cons_text['access_denied'])
        return

    await send_admin_cons_page(message, page=1)


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
    from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError

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
