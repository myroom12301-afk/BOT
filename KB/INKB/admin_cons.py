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


def build_event_link_kb(link, button_text):
    if not (link and button_text):
        return None
    builder = InlineKeyboardBuilder()
    builder.button(text=button_text, url=link)
    return builder.as_markup()


def build_user_events_list_kb(events):
    builder = InlineKeyboardBuilder()
    for event_id, title, event_date, *_ in events:
        builder.button(
            text=f"{_format_short_date(event_date)} | {title}",
            callback_data=f"important_event:{event_id}",
        )
    builder.adjust(1)
    return builder.as_markup()


def build_user_event_card_kb(event_id, link=None, button_text=None):
    builder = InlineKeyboardBuilder()
    if link and button_text:
        builder.button(text=button_text, url=link)
    builder.button(text='🔙', callback_data='important_events')
    builder.adjust(1)
    return builder.as_markup()


def build_admin_event_confirm_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text=admin_cons_text['event_publish'], callback_data='admin_event_publish')
    builder.button(text=admin_cons_text['event_cancel'], callback_data='admin_event_cancel')
    builder.adjust(1)
    return builder.as_markup()


def build_admin_events_list_kb(events):
    builder = InlineKeyboardBuilder()
    for event_id, title, event_date, *_ in events:
        builder.button(
            text=f"{_format_short_date(event_date)} | {title}",
            callback_data=f"admin_event:{event_id}",
        )
    builder.button(text=admin_cons_text['add_event'], callback_data='admin_event_add')
    builder.adjust(1)
    return builder.as_markup()


def build_admin_event_card_kb(event_id, link=None, button_text=None):
    builder = InlineKeyboardBuilder()
    if link and button_text:
        builder.button(text=button_text, url=link)
    builder.button(text=admin_cons_text['delete_event'], callback_data=f"admin_event_delete:{event_id}")
    builder.button(text=admin_cons_text['back_to_events'], callback_data='admin_event_back')
    builder.adjust(1)
    return builder.as_markup()
