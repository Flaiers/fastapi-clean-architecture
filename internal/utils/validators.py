from . import errors  # noqa


__all__ = ["validate_phone"]


def validate_phone(v: str):
    if not v.startswith(("+7", "8")) or \
            len(v.replace("+", "")) != 11:
        raise errors.PhoneError()
    return v
