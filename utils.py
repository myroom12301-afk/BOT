import re
from datetime import datetime

def is_valid_phone(phone: str) -> bool:
    phone = phone.strip()
    pattern = r'^0\d{3}([ ]?)\d{3}\1\d{3}$'
    return bool(re.fullmatch(pattern, phone))


def format_event_date(event_date: str) -> str:
    try:
        return datetime.strptime(event_date, '%Y-%m-%d').strftime('%d.%m.%Y')
    except ValueError:
        return event_date


def build_event_text(lang: str, event, labels: dict) -> str:
    _, title, event_date, description, _, _, _ = event
    return (
        f"{title}\n\n"
        f"{labels[lang]['event_date']}: {format_event_date(event_date)}\n"
        f"{labels[lang]['description']}: {description or '-'}"
    )
