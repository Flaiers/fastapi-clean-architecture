from internal.usecase.utils import errors


def validate_phone(value: str):
    if not value.startswith(("+7", "8")):
        raise errors.PhoneError()
    if len(value.replace("+", "")) != 11:
        raise errors.PhoneError()
    return value
