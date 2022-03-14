from . import consts, errors


def validate_phone(v: str):
    if not v.startswith(("+7", "8")):
        raise errors.PhoneError()
    if len(v.replace("+", "")) != consts.phone_length:
        raise errors.PhoneError()
    return v
