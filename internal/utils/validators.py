import errors


def validate_phone(v: str):
    if not v.startswith(("+7", "8")) or \
            len(v.replace("+", "")) != 11:
        raise errors.PhoneError()
    return v
