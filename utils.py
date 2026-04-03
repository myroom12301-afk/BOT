import re

def is_valid_phone(phone: str) -> bool:
    phone = phone.strip()
    pattern = r'^0\d{3}([ ]?)\d{3}\1\d{3}$'
    return bool(re.fullmatch(pattern, phone))
