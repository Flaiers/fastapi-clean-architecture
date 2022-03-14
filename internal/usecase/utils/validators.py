from . import errors

__all__ = ["validate_phone"]


def validate_phone(v: str):
    if not v.startswith(("+7", "8")):
        raise errors.PhoneError()
    if len(v.replace("+", "")) != 11:
        raise errors.PhoneError()
    return v
