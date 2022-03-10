from pydantic.errors import PydanticValueError


__all__ = ["PhoneError"]


class PhoneError(PydanticValueError):

    code = "phone"
    msg_template = "value is not a valid phone number"
