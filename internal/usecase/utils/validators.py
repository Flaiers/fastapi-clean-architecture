from internal.usecase.utils import errors


def validate_phone(v: str):
    if not v.startswith(("+7", "8")):
        raise errors.PhoneError()
    if len(v.replace("+", "")) != 11:
        raise errors.PhoneError()
    return v
