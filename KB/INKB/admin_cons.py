from datetime import datetime

from aiogram.utils.keyboard import InlineKeyboardBuilder

from TEXT.admin_cons_text import admin_cons_text


def _format_short_date(slot_date):
    # Преобразуем дату в короткий формат для текста кнопки списка.
    try:
        return datetime.strptime(slot_date, '%Y-%m-%d').strftime('%d.%m')
    except ValueError:
        return slot_date


def build_admin_cons_list_kb(bookings, page, has_next_page):
    # Строим клавиатуру списка активных записей и кнопку перехода на следующую страницу.
    builder = InlineKeyboardBuilder()

    for cons_id, slot_date, slot_time, user_id, name in bookings:
        display_name = name.strip() if str(name).strip() else admin_cons_text['no_name']
        builder.button(
            text=f"{_format_short_date(slot_date)} {slot_time} | {display_name}",
            callback_data=f"admin_cons:{cons_id}",
        )

    if has_next_page:
        builder.button(
            text=admin_cons_text['next_page'],
            callback_data=f"admin_cons_page:{page + 1}",
        )

    builder.adjust(1)
    return builder.as_markup()


def build_admin_cons_card_kb(cons_id):
    # Кнопки действий под карточкой записи администратора.
    builder = InlineKeyboardBuilder()
    builder.button(text=admin_cons_text['confirm'], callback_data=f"admin_cons_done:{cons_id}")
    builder.button(text=admin_cons_text['delete'], callback_data=f"admin_cons_delete:{cons_id}")
    builder.button(text=admin_cons_text['back_to_list'], callback_data='admin_cons_back')
    builder.adjust(2, 1)
    return builder.as_markup()
