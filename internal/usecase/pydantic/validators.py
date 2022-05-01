from typing import Pattern

from internal.usecase.pydantic import errors


def validate_phone(phone: str, regex: Pattern[str]) -> str:
    if not regex.match(phone):
        raise errors.PhoneError(phone=phone)

    return phone
